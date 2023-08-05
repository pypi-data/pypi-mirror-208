import os
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

import openai
from jinja2 import Template

from .library import Paper, clean_html
from .logging import get_logger

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)


class ChatMessage(NamedTuple):
    role: Literal["user", "system", "assistant"]
    content: Template

    def to_json(self, content: Optional[dict] = None) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content.render(**(content or {})),
        }


class OpenAiPrompt:
    def __init__(
        self,
        prompt: Union[str, List[Tuple[str, str]]],
        openai_api_key: Optional[str] = OPENAI_API_KEY,
        model: str = "text-davinci-003",
        mode: Optional[Literal["chat", "completion"]] = None,
        temperature: float = 0.5,
        max_tokens: int = 256,
    ):
        if openai_api_key is None:
            raise ValueError("No OpenAI API key provided")
        openai.api_key = openai_api_key

        self.mode = mode or (
            "chat" if model in {"gpt-4", "gpt-3.5-turbo"} else "completion"
        )
        self.model = model

        prompt = [("user", prompt)] if isinstance(prompt, str) else prompt
        self.prompt = [
            ChatMessage(role=role, content=Template(content))  # type: ignore
            for role, content in prompt
        ]

        self.temperature = temperature
        self.max_tokens = max_tokens

        self.logger = get_logger(__name__, disable_cloudwatch="yes")

    def to_json(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "mode": self.mode,
            "prompt": [message.to_json() for message in self.prompt],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def completion(self, content: dict, params: Optional[dict] = None) -> str:
        request = {
            "model": self.model,
            "prompt": self.prompt[0].content.render(**content),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **(params or {}),
        }
        response = openai.Completion.create(**request)
        self.logger.info(
            {
                "request": request,
                "response": response,
                "endpoint": "Completion",
                "action": "completion_openai_llm",
            }
        )
        return response.choices[0].text  # pyright: ignore

    def chat(self, content: dict, params: Optional[dict] = None) -> str:
        request = {
            "model": self.model,
            "messages": [message.to_json(content) for message in self.prompt],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **(params or {}),
        }
        response = openai.ChatCompletion.create(**request)
        self.logger.info(
            {
                "request": request,
                "response": response,
                "endpoint": "ChatCompletion",
                "action": "chat_openai_llm",
            }
        )
        return response.choices[0].message.content  # pyright: ignore

    def __call__(self, **content: Any) -> str:
        if self.mode == "chat":
            return self.chat(content)
        elif self.mode == "completion":
            return self.completion(content)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")


class Summary(NamedTuple):
    summary: str
    score: float
    paper: "Paper"

    @property
    def relevant(self) -> bool:
        return self.score > 0.5

    @property
    def id(self) -> str:
        return self.paper.id

    def html_format_id(self) -> str:
        return self.paper.html_format_id()

    def html_format_summary(self) -> str:
        body = "".join([f"<p>{line}</p>" for line in self.summary.split("\n")])
        title = self.paper.html_format_title()
        return f"{title}{body}"

    def format_relevant(self) -> str:
        return "✅" if self.relevant else "❌"

    def to_json(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "score": self.score,
            "paper": self.paper.to_json(),
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Summary":
        return cls(
            summary=data["summary"],
            score=data["score"],
            paper=Paper.from_json(data["paper"]),
        )


@dataclass
class Summaries:
    summaries: Dict[Tuple[str, str], Summary] = field(default_factory=dict)

    def __contains__(self, id_: str) -> bool:
        return id_ in self.summaries

    def iter(self, prompt: Optional[str] = None) -> Iterable[Summary]:
        for (_, summary_prompt), summary in self.summaries.items():
            if prompt is None or summary_prompt == prompt:
                yield summary

    def append(
        self,
        summary: Union[str, Summary],
        prompt: str = "",
        score: Optional[float] = None,
        paper: Optional[Paper] = None,
    ):
        if isinstance(summary, str):
            if score is None or paper is None:
                raise ValueError("Must provide score/paper if summary is str")
            summary = Summary(
                summary=clean_html(summary), score=score, paper=paper
            )

        self.summaries[(summary.id, prompt)] = summary

    def filter(self):
        for id_ in list(self.summaries):
            if not self.summaries[id_].relevant:
                del self.summaries[id_]

    def table(self, prompt: Optional[str] = None) -> List[List[str]]:
        if len(self.summaries) == 0:
            # must return empty list to avoid error
            return [["", "", ""]]

        return [
            [s.html_format_id(), s.html_format_summary(), s.format_relevant()]
            for s in sorted(
                list(self.iter(prompt)),
                key=lambda s: s.paper.short_id or -s.paper.score,
            )
        ]

    def to_json(self) -> Dict[str, Any]:
        return {
            "summaries": {
                f"{id_}|||{prompt}": summary.to_json()
                for (id_, prompt), summary in self.summaries.items()
            }
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Summaries":
        summaries = {}
        for key, value in data["summaries"].items():
            id_, prompt = key.split("|||", 1)
            summaries[(id_, prompt)] = Summary.from_json(value)
        return cls(summaries=summaries)
