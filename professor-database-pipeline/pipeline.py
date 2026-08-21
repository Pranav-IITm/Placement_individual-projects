"""Orchestrate webpage scraping -> LangSearch -> Gemini -> Notion."""

from __future__ import annotations

import argparse

from gemini_extractor import extract_professor
from langsearch_extractor import langsearch_extract
from notion_writer import write_professor
from scraper import fetch_webpage


def run_pipeline(url: str, write_to_notion: bool = True) -> dict:
    """Process one faculty webpage.

    External API failures are raised as clear RuntimeError messages; the pipeline
    never fabricates missing API responses.
    """
    print(f"Fetching: {url}")
    webpage_text = fetch_webpage(url)
    if not webpage_text.strip():
        raise RuntimeError("No readable text was extracted from the webpage.")

    print("Sending webpage text to LangSearch...")
    langsearch_text = langsearch_extract(webpage_text)

    print("Extracting structured fields with Gemini...")
    record = extract_professor(langsearch_text)
    record.setdefault("Website", url)

    if write_to_notion:
        print("Writing record to Notion...")
        write_professor(record)

    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Faculty webpage research database pipeline")
    parser.add_argument("url", help="Faculty webpage URL")
    parser.add_argument("--no-notion", action="store_true", help="Skip the Notion write step")
    args = parser.parse_args()

    try:
        result = run_pipeline(args.url, write_to_notion=not args.no_notion)
        print("Structured record:")
        for key, value in result.items():
            print(f"{key}: {value}")
    except Exception as exc:
        raise SystemExit(f"Pipeline failed: {exc}") from exc
