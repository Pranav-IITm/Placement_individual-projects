"""Fetch and extract readable text from faculty webpages."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.request import Request, urlopen


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


def fetch_webpage(url: str, timeout: int = 20) -> str:
    """Download HTML using only the Python standard library."""
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 research-database-pipeline/1.0"})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(content_type, errors="replace")

    parser = _TextExtractor()
    parser.feed(html)
    return "\n".join(parser.parts)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scraper.py <faculty-url>")
    print(fetch_webpage(sys.argv[1]))
