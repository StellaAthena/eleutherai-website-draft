#!/usr/bin/env python3
import csv
import html
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent
PAPERS_CSV = ROOT / "eleutherai_papers_sheet_gid2053751678.csv"
AREA_PAPERS_CSV = ROOT / "research_area_papers.csv"
TRAINING_DYNAMICS_PAGE = ROOT / "research-training-dynamics.html"

START = "<!-- AUTO-GENERATED:PAPERS:START -->"
END = "<!-- AUTO-GENERATED:PAPERS:END -->"

def parse_date(value):
    value = (value or "").strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return datetime.min


def row_date(row):
    return parse_date(row.get("Sort Date") or row.get("Release Date") or row.get("Archival Date"))


def normalize_title(title):
    return " ".join((title or "").split())


def display_year(row):
    date = row_date(row)
    return str(date.year) if date != datetime.min else ""


def display_venue(row, config):
    if config.get("display_venue"):
        return config["display_venue"]
    venue = (row.get("Conference or Journal") or row.get("Workshop") or row.get("Status") or "Paper").strip()
    if venue == "Accepted":
        return "Paper"
    return venue.replace(" (Oral)", " Oral")


def render_title(row):
    title = normalize_title(row.get("Title"))
    escaped_title = html.escape(title, quote=False)
    link = clean_link(row.get("Link") or "")
    if link:
        return f'<a href="{html.escape(link, quote=True)}">{escaped_title}</a>'
    return escaped_title


def clean_link(link):
    link = link.strip()
    if not link:
        return ""
    parts = urlsplit(link)
    if parts.netloc == "openreview.net":
        return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query.split("&referrer=", 1)[0], ""))
    return link


def render_paper(row, config):
    tags = "".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in config["tags"])
    return "\n".join(
        [
            '            <article class="paper-entry">',
            f'              <div class="label">{html.escape(display_year(row))}</div>',
            "              <div>",
            f"                <h3>{render_title(row)}</h3>",
            f'                <p>{html.escape(config["summary"])}</p>',
            f'                <div class="tag-list">{tags}</div>',
            "              </div>",
            f'              <div class="kind">{html.escape(display_venue(row, config))}</div>',
            "            </article>",
        ]
    )


def generated_training_dynamics_papers():
    with PAPERS_CSV.open(newline="") as f:
        rows = list(csv.DictReader(f))

    configs = load_area_configs("Training Dynamics")
    by_title = {normalize_title(row.get("Title")): row for row in rows}
    missing = [config["title"] for config in configs if normalize_title(config["title"]) not in by_title]
    if missing:
        raise SystemExit("Missing configured paper titles in papers CSV:\n" + "\n".join(missing))

    selected = [(by_title[normalize_title(config["title"])], config) for config in configs]
    selected.sort(key=lambda item: (row_date(item[0]), normalize_title(item[0].get("Title"))), reverse=True)
    return "\n".join(render_paper(row, config) for row, config in selected)


def load_area_configs(area):
    with AREA_PAPERS_CSV.open(newline="") as f:
        configs = []
        for row in csv.DictReader(f):
            if row.get("Research Area") != area:
                continue
            configs.append(
                {
                    "title": row["Title"],
                    "summary": row["Summary"],
                    "tags": [tag.strip() for tag in row["Tags"].split(";") if tag.strip()],
                    "display_venue": row.get("Display Venue", "").strip(),
                }
            )
    return configs


def replace_between_markers(path, generated):
    text = path.read_text()
    if START not in text or END not in text:
        raise SystemExit(f"Missing generated-content markers in {path}")
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    path.write_text(before + START + "\n" + generated + "\n" + "          " + END + after)


def main():
    replace_between_markers(TRAINING_DYNAMICS_PAGE, generated_training_dynamics_papers())


if __name__ == "__main__":
    main()
