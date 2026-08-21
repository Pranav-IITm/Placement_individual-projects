"""Notion API helpers for writing structured professor records."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _rich_text(value: str) -> dict:
    return {"rich_text": [{"text": {"content": value}}]} if value else {"rich_text": []}


def _title(value: str) -> dict:
    return {"title": [{"text": {"content": value}}]} if value else {"title": []}


def write_professor(record: dict) -> dict:
    """Create one row/page in the configured Notion database.

    Property names must match the Notion database. Unknown fields are ignored.
    """
    token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")
    if not token or not database_id:
        raise RuntimeError("NOTION_TOKEN and NOTION_DATABASE_ID must be set.")

    properties = {
        "Professor": _title(str(record.get("Professor", ""))),
        "University": _rich_text(str(record.get("University", ""))),
        "Department/Lab": _rich_text(str(record.get("Department/Lab", ""))),
        "Research Areas": _rich_text(str(record.get("Research Areas", ""))),
        "Email": _rich_text(str(record.get("Email", ""))),
        "Fit": _rich_text(str(record.get("Fit", ""))),
        "Status": _rich_text(str(record.get("Status", ""))),
        "Website": _rich_text(str(record.get("Website", ""))),
    }

    payload = {"parent": {"database_id": database_id}, "properties": properties}
    request = Request(
        "https://api.notion.com/v1/pages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": os.getenv("NOTION_VERSION", "2022-06-28"),
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Notion request failed: {exc}") from exc
