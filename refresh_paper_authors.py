#!/usr/bin/env python3

import csv
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
PAPERS_CSV = ROOT / "eleutherai_papers_sheet_gid2053751678.csv"
OUTPUT = ROOT / "data" / "research" / "paper_authors.json"


def normalize_title(title):
    return " ".join((title or "").split())


class CitationAuthorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.authors = []

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        attributes = dict(attrs)
        if attributes.get("name", "").casefold() == "citation_author":
            author = attributes.get("content", "").strip()
            if author:
                self.authors.append(author)


def fetch_authors(row):
    title = normalize_title(row.get("Title"))
    url = (row.get("Link") or "").strip()
    if not title or not url:
        return title, []
    request = Request(url, headers={"User-Agent": "EleutherAI research library metadata updater"})
    with urlopen(request, timeout=25) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = CitationAuthorParser()
    parser.feed(html)
    return title, parser.authors


def main():
    refresh_all = "--all" in sys.argv[1:]
    existing = {}
    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))

    with PAPERS_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    pending = [
        row
        for row in rows
        if row.get("Link") and (refresh_all or normalize_title(row.get("Title")) not in existing)
    ]

    failures = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_authors, row): row for row in pending}
        for future in as_completed(futures):
            row = futures[future]
            title = normalize_title(row.get("Title"))
            try:
                _, authors = future.result()
            except Exception as exc:
                failures.append((title, str(exc)))
                continue
            existing[title] = authors

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(dict(sorted(existing.items())), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    available = sum(bool(authors) for authors in existing.values())
    print(f"Author metadata available for {available} papers")
    if failures:
        print(f"Could not refresh {len(failures)} linked papers", file=sys.stderr)


if __name__ == "__main__":
    main()
