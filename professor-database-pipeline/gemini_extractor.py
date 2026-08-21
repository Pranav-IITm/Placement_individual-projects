"""Gemini API wrapper for structured professor extraction."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_FIELDS = [
    "Professor", "University", "Department/Lab", "Research Areas",
    "Email", "Fit", "Status", "Website",
]


def extract_professor(webpage_text: str, fields: list[str] | None = None) -> dict:
    """Ask Gemini to return professor information as JSON."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    fields = fields or DEFAULT_FIELDS
    schema_hint = {field: "string" for field in fields}
    prompt = (
        "Extract professor information from the webpage text below. "
        "Return ONLY valid JSON, matching this structure. Use empty strings "
        "when information is unavailable; do not invent facts.\n\n"
        f"{json.dumps(schema_hint)}\n\nWEBPAGE:\n{webpage_text}"
    )

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Gemini request failed: {exc}") from exc

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Gemini returned an unexpected response format.") from exc

    # Models occasionally wrap JSON in markdown fences despite the prompt.
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini did not return valid JSON.") from exc

    if not isinstance(data, dict):
        raise RuntimeError("Gemini JSON response is not an object.")
    return data
