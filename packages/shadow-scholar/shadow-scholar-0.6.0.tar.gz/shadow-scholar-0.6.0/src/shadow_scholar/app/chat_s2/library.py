import os
import re
from dataclasses import dataclass, field
from logging import Logger
from time import time
from typing import Dict, Iterable, List, Optional, Union

import edlib
import requests

API_FIELDS = [
    "title",
    "abstract",
    "venue",
    "fieldsOfStudy",
    "authors",
    "isOpenAccess",
    "year",
    "corpusId",
    "externalIds",
]

S2_API_KEY = os.environ.get("S2_API_KEY", "")


def clean_html(raw_html: Optional[str] = None) -> str:
    if not (raw_html := (raw_html or "").strip()):
        return raw_html

    return re.sub(
        r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});", "", raw_html
    )


def get_s2_metadata_single(
    paper: "Paper",
    s2_api_key: str = S2_API_KEY,
    logger: Optional[Logger] = None,
):
    url = (
        "https://api.semanticscholar.org/graph/v1/paper/"
        f"{paper.id}?fields={','.join(API_FIELDS)}"
    )
    header = {"x-api-key": s2_api_key}
    response = requests.get(url, headers=header)
    paper.metadata.update(response.json())


def get_s2_metadata(
    papers: Iterable["Paper"],
    s2_api_key: str = S2_API_KEY,
    logger: Optional[Logger] = None,
):
    start = time()

    url = (
        "https://api.semanticscholar.org/graph/v1/paper/batch?"
        f"fields={','.join(API_FIELDS)}"
    )
    header = {"x-api-key": s2_api_key}

    papers_with_missing_metadata = [p for p in papers if p.missing]

    if not papers_with_missing_metadata:
        # nothing new to fetch metadata for
        return

    data = {"ids": [p.id for p in papers_with_missing_metadata]}
    response = requests.post(url, headers=header, json=data)
    results = response.json()

    if (
        isinstance(results, dict)
        and results.get("message") == "Internal Server Error"
    ):
        for paper in papers_with_missing_metadata:
            get_s2_metadata_single(paper, s2_api_key, logger)
        return

    # responses might not in order of request, so we need to match them up;
    # we do this by calculating similarity
    for paper in papers_with_missing_metadata:
        distance: List[int] = []
        for result in results:
            if (
                paper.id == result.get("paperId", None)
                or paper.id == result.get("corpusId", None)
                or str(paper.id).split(":", 1)[-1]
                in result.get("externalIds", {}).values()
            ):
                distance.append(0)
                break

            elif "title" in result and "title" in paper.metadata:
                distance.append(
                    edlib.align(paper.metadata["title"], result["title"])[
                        "editDistance"
                    ]
                )
            else:
                distance.append(1000)

        if len(distance) > 0 and (best_guess := min(distance)) < 1000:
            location = distance.index(best_guess)
            metadata = results.pop(location)
            paper.metadata.update(metadata)

    delta = time() - start
    logger.info(
        {
            "url": url,
            "data": data,
            "elapsed": delta,
            "response": results,
            "action": "get_s2_metadata",
        }
    ) if logger else None


@dataclass
class Paper:
    id: str
    metadata: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Paper({self.id})"

    @classmethod
    def id_from_s2_url(cls, url: str) -> Union[str, None]:
        is_valid_url = re.match(
            r"https://(www.)?semanticscholar.org/paper.*?/([a-f0-9]+)", url
        )
        if not is_valid_url:
            return None

        sha1 = is_valid_url.group(2)
        return sha1

    @classmethod
    def id_from_arxiv_url(cls, url: str) -> Union[str, None]:
        is_valid_url = re.match(r"https://(www.)?arxiv.org/abs/(.+)", url)
        if not is_valid_url:
            return None

        arxiv_id = is_valid_url.group(2)
        return f"arxiv:{arxiv_id}"

    @classmethod
    def from_url(cls, url: str, **attrs) -> Optional["Paper"]:
        id_ = cls.id_from_s2_url(url) or cls.id_from_arxiv_url(url)
        return cls(id_, metadata=attrs) if id_ else None

    @property
    def short_id(self) -> Optional[int]:
        if short_id := self.metadata.get("short_id", None):
            short_id = int(short_id)
        return short_id

    @property
    def score(self) -> float:
        return self.metadata.get("score", -1.0)

    @property
    def missing(self) -> bool:
        return self.metadata.get("corpusId", None) is None

    @property
    def authors(self) -> List[str]:
        return [author["name"] for author in self.metadata.get("authors", [])]

    @property
    def url(self) -> str:
        return f"https://api.semanticscholar.org/{self.id}"

    @property
    def year(self) -> Union[int, None]:
        if (year := self.metadata.get("year")) is not None:
            year = int(year)
        return year

    @property
    def title(self) -> str:
        return clean_html(self.metadata.get("title", ""))

    @property
    def abstract(self) -> str:
        return clean_html(self.metadata.get("abstract", ""))

    @property
    def is_open_access(self) -> bool:
        return self.metadata.get("isOpenAccess", False)

    @property
    def venue(self) -> str:
        return self.metadata.get("venue", "")

    @property
    def corpus_id(self) -> str:
        return self.metadata.get("corpusId", "")

    def _truncate(self, text: str, cols: int = 70) -> str:
        if len(text) > (cols - 3):
            return text[:cols] + "..."
        return text

    def html_format_title(self) -> str:
        return (
            f'<a href="{self.url}" target="_blank">'
            f"<b>{self._truncate(self.title)}</b></a> ({self.year})"
        )

    def html_format_paper(self) -> str:
        title = self.html_format_title()
        authors = f'<p><i>{self._truncate(", ".join(self.authors))}</i></p>'
        abstract = f'<p>{self._truncate(self.abstract or "")}</p>'
        return "\n".join([title, authors, abstract])

    def html_format_id(self) -> str:
        short_id = (
            f'<span class="span-major">[{self.short_id}]</span>'
            if self.short_id
            else ""
        )

        span_class = "span-minor" if short_id else "span-minor"
        title_id = (
            f'<span class="{span_class}">'
            f'<a href="{self.url}" target="_blank">{self.corpus_id}</a>'
            "</span>"
        )
        score = f"<i>{self.score:.2f}</i>"
        return (
            '<div id="id-score-table-container">'
            f"<p>{short_id}</p><p>{title_id}</p>"
            f'<p id="score-para">{score}</p>'
            "</div>"
        )

    def to_json(self):
        return {
            "id": self.id,
            "metadata": self.metadata,
            "short_id": self.short_id,
        }

    @classmethod
    def from_json(cls, data):
        return cls(**data)


@dataclass
class Stack:
    papers: Dict[str, Paper] = field(default_factory=dict)
    s2_api_key: str = S2_API_KEY

    def _compute_short_ids(self):
        for i, p in enumerate(self.papers.values(), start=1):
            if p.short_id is None:
                p.metadata["short_id"] = i

    def append(self, paper: Paper):
        if paper.id not in self.papers:
            self.papers[paper.id] = paper
            self._compute_short_ids()

    def extend(self, papers: Iterable[Paper]):
        for paper in papers:
            self.append(paper)

    def fetch(self):
        get_s2_metadata(self.papers.values(), s2_api_key=self.s2_api_key)
        for pid in list(self.papers):
            # remove papers that are not found
            if self.papers[pid].missing:
                del self.papers[pid]
        self._compute_short_ids()

    @property
    def sorted(self) -> List[Paper]:
        return sorted(self.papers.values(), key=lambda p: -p.score)

    def __len__(self):
        return len(self.papers)

    def __getitem__(self, key):
        return self.papers[key]

    def __iter__(self):
        return iter(self.papers)

    def __str__(self) -> str:
        return (
            f"Stack_{len(self.papers)}(\n"
            + "\n".join(f"\t{paper}," for paper in self.papers)
            + "\n)"
        )

    def table(self) -> List[List[str]]:
        if len(self) == 0:
            # we need to return something otherwise UI will break
            return [["", ""]]

        return [
            [p.html_format_id(), p.html_format_paper()]
            for p in sorted(
                self.sorted, key=lambda p: (p.short_id or -p.score)
            )
        ]

    def to_json(self):
        return [p.to_json() for p in self.papers.values()]

    @classmethod
    def from_json(cls, data):
        return cls(papers={p["id"]: Paper.from_json(p) for p in data})
