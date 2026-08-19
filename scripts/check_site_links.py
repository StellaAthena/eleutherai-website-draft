#!/usr/bin/env python3
"""Check generated HTML references to local pages and assets."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


REFERENCE_ATTRIBUTES = {
    "a": ("href",),
    "img": ("src", "srcset"),
    "link": ("href",),
    "script": ("src",),
    "source": ("src", "srcset"),
    "video": ("src", "poster"),
}
EXTERNAL_SCHEMES = {"data", "http", "https", "mailto", "tel", "javascript"}


class ReferenceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for attribute in REFERENCE_ATTRIBUTES.get(tag, ()):
            value = values.get(attribute, "").strip()
            if not value:
                continue
            if attribute == "srcset":
                self.references.extend(item.strip().split()[0] for item in value.split(",") if item.strip())
            else:
                self.references.append(value)


def candidate_paths(root, page, reference):
    path = unquote(urlsplit(reference).path)
    if not path:
        return []
    target = root / path.lstrip("/") if path.startswith("/") else page.parent / path
    candidates = [target]
    if target.suffix == "":
        candidates.extend((target / "index.html", target.with_suffix(".html")))
    return candidates


def broken_references(root):
    broken = []
    for page in root.rglob("*.html"):
        parser = ReferenceParser()
        parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        for reference in parser.references:
            parsed = urlsplit(reference)
            if parsed.scheme in EXTERNAL_SCHEMES or parsed.netloc or reference.startswith("//"):
                continue
            candidates = candidate_paths(root, page, reference)
            if candidates and not any(candidate.exists() for candidate in candidates):
                broken.append((page.relative_to(root), reference))
    return broken


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    args = parser.parse_args()
    failures = []
    for root in args.roots:
        if not root.is_dir():
            failures.append(f"missing build directory: {root}")
            continue
        failures.extend(f"{root}/{page}: {reference}" for page, reference in broken_references(root))
    if failures:
        raise SystemExit("Broken local references:\n" + "\n".join(failures))
    print("Local page and asset references passed")


if __name__ == "__main__":
    main()
