import os
import re
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import List, Tuple, Union

from shadow_scholar.cli import Argument, cli, safe_import

with safe_import():
    import gradio as gr

    from .library import Paper, Stack
    from .llm import OpenAiPrompt, Summaries
    from .logging import get_logger
    from .search import BaseSearchEndpoint, GoogleSearchEndpoint, Queries


ConversationType = List[Tuple[Union[str, None], Union[str, None]]]


SEARCH_URI = "https://api.semanticscholar.org/graph/v1/paper/search/"
CSS_URI = Path(__file__).parent / "res" / "style.css"
LOGO_URI = Path(__file__).parent / "res" / "logo.svg"
JAVASCRIPT_URI = Path(__file__).parent / "res" / "script.js"

DESCRIPTION = """\
<div id="description">
    <div id="description-header">
        <h1>
            <span id="header-logo">{svg_logo}</span>
            <span id="header-text">Talk to Shadow Scholar</span>
        </h1>
    </div>
    <p>
        This is a demo of a chatbot that uses the <a target="_blank" \
        href="https://semanticscholar.org/">Semantic Scholar</a> API to \
        answer questions about scientific papers.You can either provide \
        it a list of papers to use, or ask the virtual scholar to search \
        papers for you.
    </p>
    <p>
        This virtual scholar is powered by the <a target="_blank" \
        href="https://platform.openai.com/docs/models/gpt-3">OpenAI API \
        </a> and uses the <code>{model}</code> model. It is intended as a \
        research prototype, <b>do not use it to power any user-facing \
        applications</b>.
    </p>
</div>
"""


QUERY_EXTRACTION_TEMPLATE = """\
I need help finding academic papers about the following topic: "{{ prompt }}".

I have access to an intelligent search engine that can find papers on the \
topic above. Could you suggest one or more queries to use? A few rules:
- Write them as a list, starting with "-".
- Suggest at most {% if cnt > 1 %}{{ cnt }} queries\
{% else %}one query{% endif %}.
- Avoid repetitive queries.
- Shorter queries are better.
- Do not use boolean operators, such as AND, OR, NOT, in the queries.
"""


ANSWER_FORMULATION_TEMPLATE = """\
I am interested in learning more about the following question: "{{ prompt }}".

Using the following evidence summaries I have summarized from papers:
{% for summary in summaries %}\
[{{ summary.paper.short_id }}] {{ summary.summary }}
{% endfor %}\

Could you answer the question? A few rules:
- Please cite the relevant snippet(s) using the format [n] \
(for example, [{{ summaries[0].paper.short_id }}] for the first snippet).
- Do not write a claim unless it appears in one of the snippets.
- If a snippet is not relevant, do not use it.
- You must be as brief and concise as possible; do not write more than \
five sentences.
- You must explain your reasoning.
- If none of the snippets contain a good answer, say that you can't answer \
the question.
"""

RESULTS_SUMMARIZATION_TEMPLATE = """\
I am interested in learning more about the following topic: \
"{{ prompt }}".

Does the following text contain any relevant information on the topic?

{{ paper.title }} ({{ paper.year }})
{{ " ".join(paper.authors) }}
{{ paper.abstract }}

If it does contain relevant information, write down one short sentences \
explaining why; do not start with "relevant". If the passage is not relevant, \
respond with "not relevant".
"""


def search_and_table(
    state: "State",
    max_results: Union[int, float],
    endpoint: "BaseSearchEndpoint",
) -> Tuple[List[List[str]], "State"]:
    searches = []
    max_results = int(max_results)
    for query in state.queries.use(max_results):
        results = endpoint(query, max_results=max_results)
        state.stack.extend(results)
        searches.append({"query": query, "results": [p.id for p in results]})

    state.stack.fetch()

    state.logger.info(
        {
            "searches": searches,
            "action": "search_and_table",
            "endpoint": endpoint.to_json(),
        }
    )

    return state.stack.table(), state


def add_user_paper_to_chatbot(
    paper_id: str, state: "State"
) -> Tuple[str, List[List[str]], "State"]:
    paper = (
        Paper.from_url(url=paper_id)
        if paper_id.startswith("http")
        else Paper(id=paper_id)
    )
    if paper is not None:
        state.stack.append(paper)
        state.stack.fetch()

    state.logger.info(
        {
            "action": "add_user_paper_to_chatbot",
            "paper_id": paper_id,
            "paper": paper.id if paper is not None else None,
        }
    )

    return "", state.stack.table(), state


def add_user_query_to_chatbot(
    query: str, state: "State"
) -> Tuple[str, ConversationType, "State"]:
    if query := query.strip():
        state.queries.add([(query, None)])

    state.logger.info(
        {
            "action": "add_user_query_to_chatbot",
            "query": query,
        }
    )
    return "", state.queries.list(), state


def make_queries_from_prompt(
    user_prompt: str,
    cnt_query: Union[int, float],
    state: "State",
    model: "OpenAiPrompt",
) -> Tuple[ConversationType, "State"]:
    if not (user_prompt := user_prompt.strip()):
        return state.queries.list(), state

    completion = model(prompt=user_prompt, cnt=int(cnt_query))
    extracted_queries = [
        strip_and_remove_quotes(q) for q in completion.split("\n") if q.strip()
    ]
    state.queries.add([(None, q) for q in extracted_queries])

    state.logger.info(
        {
            "action": "make_queries_from_prompt",
            "user_prompt": user_prompt,
            "cnt_query": cnt_query,
            "queries": extracted_queries,
        }
    )
    return state.queries.list(), state


def strip_and_remove_quotes(text: str) -> str:
    text = re.sub(r"^\-\s*", "", text)
    text = re.sub(r"[\"\']+", "", text)
    text = re.sub(r"(^\s+|\s+$)", "", text)
    return text


def summarize_results(
    prompt: str, state: "State", model: "OpenAiPrompt"
) -> Tuple[List[List[str]], "State"]:
    if not (prompt := prompt.strip()):
        return state.summaries.table(), state

    for paper in state.stack.papers.values():
        if paper.id in state.summaries:
            continue
        summary = model(paper=paper, prompt=prompt)
        not_relevant = re.search(
            r"^((non|not) relevant|irrelevant)\.*?\s?", summary, re.I
        )
        score = 0.0 if not_relevant else 1.0
        summary = re.sub(
            r"(^relevant.*?)([a-zA-Z])", r"\2", summary, flags=re.I
        )
        state.summaries.append(
            summary=summary, prompt=prompt, score=score, paper=paper
        )

    state.logger.info(
        {
            "action": "summarize_results",
            "prompt": prompt,
            "summaries": [
                {"paper": s.id, "summary": s.summary}
                for s in state.summaries.iter(prompt)
            ],
        }
    )
    return state.summaries.table(), state


def compute_answer_from_summaries(
    prompt: str,
    state: "State",
    model: "OpenAiPrompt",
) -> Tuple[str, "State"]:
    if not (prompt := prompt.strip()):
        return "Please provide a prompt", state

    relevant_summaries = [
        s for s in state.summaries.iter(prompt) if s.relevant
    ]

    if not relevant_summaries:
        return "No relevant summaries found", state

    answer = model(prompt=prompt, summaries=relevant_summaries)

    state.logger.info(
        {
            "action": "compute_answer_from_summaries",
            "prompt": prompt,
            "answer": answer,
        }
    )

    return answer, state


def run_all_fn(
    prompt: str,
    cnt_query: int,
    max_results: int,
    state: "State",
    search_endpoint: "BaseSearchEndpoint",
    query_prompt_model: "OpenAiPrompt",
    answer_prompt_model: "OpenAiPrompt",
    results_summarization: "OpenAiPrompt",
):
    state = State.new()

    # make queries from prompt
    queries, state = make_queries_from_prompt(
        user_prompt=prompt,
        cnt_query=cnt_query,
        state=state,
        model=query_prompt_model,
    )

    # search for papers
    results, state = search_and_table(
        state=state,
        max_results=max_results,
        endpoint=search_endpoint,
    )

    # summarize results
    summaries, state = summarize_results(
        prompt=prompt,
        state=state,
        model=results_summarization,
    )

    # compute answer
    output, state = compute_answer_from_summaries(
        prompt=prompt,
        state=state,
        model=answer_prompt_model,
    )

    return [queries, results, summaries, output, state]


def clear_all():
    state = State.new()
    return (
        "",
        "",
        state.queries.list(),
        state.stack.table(),
        state.summaries.table(),
        state,
    )


def rate_feedback(prompt: str, output: str, state: "State", score: int):
    state.logger.warn(
        {
            "action": "rate_feedback_interaction",
            "prompt": prompt,
            "output": output,
            "score": score,
            "state": state.to_json(),
        }
    )


@dataclass
class State:
    stack: "Stack"
    queries: "Queries"
    summaries: "Summaries"

    def __post_init__(self):
        self.logger = get_logger(__name__)

    @classmethod
    def new(cls) -> "State":
        return State(stack=Stack(), queries=Queries(), summaries=Summaries())

    def to_json(self):
        return {
            "stack": self.stack.to_json(),
            "queries": self.queries.to_json(),
            "summaries": self.summaries.to_json(),
        }

    @classmethod
    def from_json(cls, json):
        return cls(
            stack=Stack.from_json(json["stack"]),
            queries=Queries.from_json(json["queries"]),
            summaries=Summaries.from_json(json["summaries"]),
        )


@cli(
    "app.chat_s2",
    arguments=[
        Argument(
            "-sp",
            "--server-port",
            default=7860,
            help="Port to run the server on",
        ),
        Argument(
            "-sn",
            "--server-name",
            default="localhost",
            help="Server address to run the gradio app at",
        ),
        Argument(
            "-llm",
            "--llm-model",
            default="gpt-3.5-turbo",
            help="Language model to use for the chatbot",
        ),
        Argument(
            "-ok",
            "--openai-key",
            default=os.environ.get("OPENAI_API_KEY"),
            help="OpenAI API key",
        ),
        Argument(
            "-sk",
            "--s2-key",
            default=os.environ.get("S2_API_KEY"),
            help="Semantic Scholar API key",
        ),
        Argument(
            "-gk",
            "--google-custom-search-key",
            default=os.environ.get("GOOGLE_CUSTOM_SEARCH_API_KEY"),
        ),
    ],
    requirements=[
        "requests",
        "openai",
        "jinja2",
        "gradio>=3.23.0",
        "watchtower",
        "logging_json",
        "edlib",
    ],
)
def run_v2_demo(
    server_port: int,
    server_name: str,
    openai_key: str,
    llm_model: str,
    s2_key: str,
    google_custom_search_key: str,
):
    assert openai_key is not None, "OpenAI API key is required"
    assert s2_key is not None, "Semantic Scholar API key is required"
    assert (
        google_custom_search_key is not None
    ), "Google Custom Search API key is required"

    search_endpoint = GoogleSearchEndpoint(api_key=google_custom_search_key)

    with open(CSS_URI, "r") as f:
        css_gradio = f.read()

    with open(LOGO_URI) as f:
        svg_logo = f.read()

    with gr.Blocks(
        title="Talk to Shadow Scholar ",
        css=css_gradio,
        analytics_enabled=False,
    ) as demo:
        gr.HTML(DESCRIPTION.format(svg_logo=svg_logo, model=llm_model))
        state = gr.State(State.new)  # pyright: ignore

        with gr.Row(variant="panel"):
            with gr.Column(scale=3):
                run_all = gr.Button(
                    "Run End-to-End",
                    variant="primary",
                    elem_id="run-end-to-end",
                )
                prompt = gr.Textbox(
                    interactive=True,
                    label="Prompt",
                    lines=5,
                    max_lines=5,
                    placeholder="What would you like to know about?",
                )

            with gr.Column(scale=3):
                clear = gr.Button("Clear All", variant="stop")
                output = gr.Textbox(
                    interactive=False,
                    label="Output",
                    lines=5,
                    placeholder="Provide a prompt to get started",
                )

            with gr.Column(min_width=50):
                gr.HTML('<div id="rate-text">Rate Output</div>')
                with gr.Row(variant="compact"):
                    feedback_positive = gr.Button("👍")
                    feedback_negative = gr.Button("👎")

        gr.Markdown("## 1️⃣ Search Pipeline")
        with gr.Row(variant="panel"):
            with gr.Column(scale=1, min_width=200):
                with gr.Row():
                    with gr.Column(min_width=100):
                        make_queries = gr.Button(
                            "Get Queries",
                            elem_classes="match-height",
                            elem_id="get-queries",
                        )
                    with gr.Column(min_width=50):
                        cnt_query = gr.Number(
                            value=2,
                            label="Max Queries",
                            show_label=False,
                            precision=0,
                        )

                queries = gr.Chatbot(label="Queries")
                query_box = gr.Textbox(
                    lines=1,
                    interactive=True,
                    label="Add Query",
                    placeholder="Type a query and press enter...",
                )

            with gr.Column(scale=2, min_width=300):
                with gr.Row():
                    search = gr.Button(
                        "Search",
                        elem_classes="match-height",
                        elem_id="search",
                    )
                    max_results = gr.Number(
                        value=5,
                        label="Max Results",
                        show_label=False,
                        precision=0,
                    )

                results = gr.DataFrame(
                    headers=["ID", "Paper"],
                    value=[["", ""]],
                    col_count=2,
                    interactive=False,
                    type="array",
                    datatype="markdown",
                    wrap=True,
                    overflow_row_behaviour="paginate",
                )
                paper_box = gr.Textbox(
                    lines=1,
                    interactive=True,
                    label="Add Paper from Semantic Scholar",
                    placeholder="Paste a paper ID or URL...",
                )

        gr.Markdown("## 2️⃣ Rank and Summarize")
        with gr.Row(variant="panel"):
            with gr.Column():
                summarize = gr.Button(
                    value="Summarize Results", elem_id="summarize-results"
                )
                summaries = gr.DataFrame(
                    headers=["Paper", "Summary", "Relevant?"],
                    value=[["", "", ""]],
                    col_count=3,
                    interactive=False,
                    type="array",
                    datatype="markdown",
                    wrap=True,
                    overflow_row_behaviour="paginate",
                )
                compute_answer = gr.Button(
                    value="Compute Answer", elem_id="compute-answer"
                )

        # llm calls
        query_prompt_model = OpenAiPrompt(
            prompt=QUERY_EXTRACTION_TEMPLATE,
            openai_api_key=openai_key,
            model=llm_model,
            temperature=0.7,
        )
        answer_prompt_model = OpenAiPrompt(
            prompt=ANSWER_FORMULATION_TEMPLATE,
            openai_api_key=openai_key,
            model=llm_model,
        )
        results_summarization = OpenAiPrompt(
            prompt=RESULTS_SUMMARIZATION_TEMPLATE,
            openai_api_key=openai_key,
            model=llm_model,
            temperature=0.5,
            max_tokens=128,
        )
        # connect all components here after rendering the UI

        # This allows users to add queries
        query_box.submit(
            add_user_query_to_chatbot,
            [query_box, state],
            [query_box, queries, state],
        )

        paper_box.submit(
            add_user_paper_to_chatbot,
            [paper_box, state],
            [paper_box, results, state],
        )

        # This allows users to automatically generate queries from a prompt
        make_queries.click(
            partial(
                make_queries_from_prompt,
                model=query_prompt_model,
            ),
            [prompt, cnt_query, state],
            [queries, state],
        )

        # this uses google custom search to search for papers
        search.click(
            partial(search_and_table, endpoint=search_endpoint),
            [state, max_results],
            [results, state],
        )

        # this uses gpt to get summaries
        summarize.click(
            partial(summarize_results, model=results_summarization),
            [prompt, state],
            [summaries, state],
        )

        # this gets the final answer
        compute_answer.click(
            partial(compute_answer_from_summaries, model=answer_prompt_model),
            [prompt, state],
            [output, state],
        )

        clear.click(
            clear_all,
            [],
            [prompt, output, queries, results, summaries, state],
        )

        run_all.click(
            partial(
                run_all_fn,
                search_endpoint=search_endpoint,
                query_prompt_model=query_prompt_model,
                answer_prompt_model=answer_prompt_model,
                results_summarization=results_summarization,
            ),
            [prompt, cnt_query, max_results, state],
            [queries, results, summaries, output, state],
        )

        feedback_positive.click(
            partial(rate_feedback, score=1), [prompt, output, state]
        )
        feedback_negative.click(
            partial(rate_feedback, score=-1), [prompt, output, state]
        )

    try:
        demo.launch(
            server_name=server_name,
            server_port=server_port,
            show_api=False,
        )
    except Exception as e:
        gr.close_all()
        raise e
