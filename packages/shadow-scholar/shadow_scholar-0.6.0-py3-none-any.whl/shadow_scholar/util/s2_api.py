"""

@lucas, @kylel

"""

import os
from logging import Logger
from time import time
from typing import Iterable, Optional

from shadow_scholar.cli import require, safe_import

with safe_import():
    import requests

S2_API_KEY = os.environ.get("S2_API_KEY", "")

API_FIELDS = [
    "title",
    "abstract",
    "venue",
    "fieldsOfStudy",
    "authors",
    "isOpenAccess",
    "year",
    "corpusId",
]


@require(["requests"])
def get_s2_metadata(
    paper_ids: Iterable[str],
    s2_api_key: str = S2_API_KEY,
    logger: Optional[Logger] = None,
):
    start = time()

    url = (
        "https://api.semanticscholar.org/graph/v1/paper/batch?"
        f"fields={','.join(API_FIELDS)}"
    )
    header = {"x-api-key": s2_api_key}

    data = {"ids": list(paper_ids)}
    response = requests.post(url, headers=header, json=data)
    results = response.json()

    delta = time() - start
    logger.info(
        {
            "url": url,
            "data": data,
            "elapsed": delta,
            "response": response,
            "action": "get_s2_metadata",
        }
    ) if logger else None

    return results
