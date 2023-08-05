import argparse
import json
import os
import re
import urllib.parse
from dataclasses import dataclass, field
from time import time
from typing import (
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

import requests

from .library import S2_API_KEY, Paper, get_s2_metadata
from .logging import get_logger

S2_SEARCH_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search/"
GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY", "")


class BaseSearchEndpoint:
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.logger = get_logger(__name__, disable_cloudwatch="yes")

    def to_json(self) -> Dict[str, str]:
        return {"endpoint": self.endpoint, "name": self.__class__.__name__}

    def encode(self, text: str) -> str:
        text = re.sub(r"^\-\s*", "", text)
        text = re.sub(r"[\"\']+", "", text)
        text = re.sub(r"(^\s+|\s+$)", "", text)
        return text

    def __call__(self, query: str, max_results: int = 1000) -> List[Paper]:
        raise NotImplementedError()


class S2SearchEndpoint(BaseSearchEndpoint):
    def __init__(
        self,
        endpoint: str = S2_SEARCH_ENDPOINT,
        api_key: str = S2_API_KEY,
    ):
        super().__init__(endpoint=endpoint, api_key=api_key)

    def encode(self, text: str) -> str:
        text = super().encode(text)
        return text.replace(" ", "+")

    def __call__(self, query: str, max_results: int = 1000) -> List[Paper]:
        start = time()
        query = self.encode(query)
        url = f"{self.endpoint}?query={query}"
        headers = {"x-api-key": self.api_key}
        response = requests.get(url, headers=headers).json()
        end = time()
        self.logger.info(
            {
                "action": "s2_search",
                "query": query,
                "elapsed": end - start,
                "response": response,
            }
        )

        papers = [
            Paper(
                p["paperId"], metadata={"score": 1.0 / i, "title": p["title"]}
            )
            for i, p in enumerate(response.get("data", []))
        ]
        return papers[:max_results]


class GoogleSearchEndpoint(BaseSearchEndpoint):
    def __init__(
        self,
        endpoint: str = "https://www.googleapis.com/customsearch/v1",
        api_key: str = GOOGLE_SEARCH_API_KEY,
        cx: str = "602714345f3a24773",
    ):
        super().__init__(endpoint=endpoint, api_key=api_key)
        self.cx = cx

    def encode(self, text: str) -> str:
        text = super().encode(text)
        return urllib.parse.quote(text)

    def __call__(self, query: str, max_results: int = 1000) -> List[Paper]:
        start = time()
        query = self.encode(query)
        url = (
            f"https://www.googleapis.com/customsearch/v1/siterestrict?"
            f"&key={self.api_key}"
            f"&cx={self.cx}"
            f"&q={query}"
        )
        response = requests.get(url).json()
        end = time()

        self.logger.info(
            {
                "action": "google_search",
                "query": query,
                "elapsed": end - start,
                "response": response,
            }
        )
        papers = [
            Paper.from_url(url=r["link"], score=1.0 / i, title=r["title"])
            for i, r in enumerate(
                cast(list, response.get("items", [])), start=1
            )
        ]
        filtered = [p for p in papers if p is not None][:max_results]
        return filtered


class Query(NamedTuple):
    user_query: Union[str, None]
    system_query: Union[str, None]

    def __bool__(self):
        return self.text != ""

    @property
    def text(self) -> str:
        return self.user_query or self.system_query or ""

    def to_json(self) -> Dict[str, Union[str, None]]:
        return {
            "user_query": self.user_query,
            "system_query": self.system_query,
        }

    @classmethod
    def from_json(cls, data: Dict[str, Union[str, None]]):
        return cls(**data)


@dataclass
class Queries:
    queries: Dict[str, Query] = field(default_factory=dict)
    used: Set[Tuple[str, Optional[int]]] = field(default_factory=set)

    def add(self, queries: List[Tuple[Union[str, None], Union[str, None]]]):
        for query in queries:
            query = Query(*query)
            if not query:
                continue
            self.queries[query.text] = query

    def use(self, num_results: Optional[int] = None) -> Iterable[str]:
        for query in self.queries:
            key = (query, num_results)
            if key not in self.used:
                self.used.add(key)
                yield query

    def list(self) -> List[Tuple[Union[str, None], Union[str, None]]]:
        return list(self.queries.values())

    def to_json(
        self,
    ) -> Dict[str, List[Tuple[Union[str, None], Union[str, None]]]]:
        return {"queries": self.list()}

    @classmethod
    def from_json(
        cls, data: Dict[str, List[Tuple[Union[str, None], Union[str, None]]]]
    ):
        queries = cls()
        queries.add(data["queries"])
        return queries


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-e",
        "--endpoint",
        type=str,
        default="google",
        choices=["google", "s2"],
    )
    ap.add_argument("-q", "--query", type=str, required=True)
    ap.add_argument("-m", "--max_results", type=int, default=1000)
    args = ap.parse_args()

    endpoint: BaseSearchEndpoint
    if args.endpoint == "google":
        endpoint = GoogleSearchEndpoint()
    elif args.endpoint == "s2":
        endpoint = S2SearchEndpoint()
    else:
        raise ValueError(f"Unknown endpoint {args.endpoint}")

    papers = endpoint(args.query, max_results=args.max_results)
    get_s2_metadata(papers)
    print(json.dumps([p.to_json() for p in papers], indent=2))
    print(
        f"Found {sum(1 for p in papers if not p.missing):,} papers"
        f" with metadata out of {len(papers):,} total"
    )
