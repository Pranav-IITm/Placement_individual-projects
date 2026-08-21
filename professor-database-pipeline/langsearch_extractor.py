"""Minimal LangSearch API wrapper.

The endpoint can be changed with LANGSEARCH_API_URL if the provider's API
configuration differs. No API credentials are stored in this repository.
"""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LANGSEARCH_API_URL = os.getenv("LANGSEARCH_API_URL", "https://api.langsearch.com/v1/chat/completions")


def langsearch_extract(webpage_text: str, prompt: str | None = None) -> str:
    """Send webpage text to LangSearch and return its textual response."""
    api_key = os.getenv("LANGSEARCH_API_KEY")
    if not api_key:
        raise RuntimeError("LANGSEARCH_API_KEY is not set.")

    payload = {
        "model": os.getenv("LANGSEARCH_MODEL", "langsearch"),
        "messages": [
            {
                "role": "user",
                "content": prompt or "Extract useful factual information from this faculty webpage:\n\n" + webpage_text,
            }
        ],
    }
    request = Request(
        LANGSEARCH_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"LangSearch request failed: {exc}") from exc

    try:
        return result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("LangSearch returned an unexpected response format.") from exc
