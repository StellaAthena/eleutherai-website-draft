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
HOMEPAGE = ROOT / "index.html"
HOMEPAGE_PAPER_LIMIT = 5

PAPERS_START = "<!-- AUTO-GENERATED:PAPERS:START -->"
PAPERS_END = "<!-- AUTO-GENERATED:PAPERS:END -->"
HOMEPAGE_PAPERS_START = "<!-- AUTO-GENERATED:HOMEPAGE-PAPERS:START -->"
HOMEPAGE_PAPERS_END = "<!-- AUTO-GENERATED:HOMEPAGE-PAPERS:END -->"

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


def pub_date(row):
    return parse_date(row.get("Pub Date"))


def normalize_title(title):
    return " ".join((title or "").split())


def display_year(row):
    date = row_date(row)
    return str(date.year) if date != datetime.min else ""


def display_full_date(date):
    if date == datetime.min:
        return ""
    return f"{date.day} {date.strftime('%B %Y')}"


def display_venue(row, config):
    if config.get("display_venue"):
        return config["display_venue"]
    venue = (row.get("Conference or Journal") or row.get("Workshop") or row.get("Status") or "Paper").strip()
    if venue == "Accepted":
        return "Paper"
    return venue.replace(" (Oral)", " Oral")


def display_homepage_venue(row):
    status = (row.get("Status") or "").strip().casefold()
    conference = (row.get("Conference or Journal") or "").strip()
    workshop = (row.get("Workshop") or "").strip()
    if status == "accepted":
        venue = conference or workshop
    elif conference:
        venue = workshop or "arXiv"
    else:
        venue = "arXiv"
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


def render_homepage_paper(row, is_open=False):
    date = pub_date(row)
    title = normalize_title(row.get("Title"))
    venue = display_homepage_venue(row)
    link = clean_link(row.get("Link") or "")
    areas = []
    for value in (row.get("Primary Area"), row.get("Additional Area")):
        value = (value or "").strip()
        if value and value not in areas:
            areas.append(value)
    meta = []
    if areas:
        meta.append("Area: " + ", ".join(areas))
    lead_org = (row.get("Lead Org") or "").strip()
    if lead_org:
        meta.append("Lead org: " + lead_org)
    poc = (row.get("EleutherAI PoC") or "").strip()
    if poc:
        meta.append("EleutherAI contact: " + poc)

    title_html = html.escape(title, quote=False)
    if link:
        title_html = f'<a href="{html.escape(link, quote=True)}">{title_html}</a>'

    lines = [
        f'          <details class="publication-item"{ " open" if is_open else "" }>',
        "            <summary>",
        f'              <span class="publication-date">{html.escape(display_full_date(date))}</span>',
        f'              <span class="publication-title">{title_html}</span>',
        f'              <span class="publication-venue">{html.escape(venue)}</span>',
        "            </summary>",
    ]
    if meta:
        lines.append(f"            <p>{html.escape('. '.join(meta))}.</p>")
    if link:
        lines.append(f'            <a class="link" href="{html.escape(link, quote=True)}">Read paper</a>')
    lines.append("          </details>")
    return "\n".join(lines)


def generated_homepage_papers(limit=HOMEPAGE_PAPER_LIMIT):
    with PAPERS_CSV.open(newline="") as f:
        rows = [
            row
            for row in csv.DictReader(f)
            if normalize_title(row.get("Title")) and pub_date(row) != datetime.min
        ]
    rows.sort(key=lambda row: (pub_date(row), normalize_title(row.get("Title"))), reverse=True)
    return "\n".join(render_homepage_paper(row, is_open=i == 0) for i, row in enumerate(rows[:limit]))


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


def replace_between_markers(path, generated, start, end):
    text = path.read_text()
    if start not in text or end not in text:
        raise SystemExit(f"Missing generated-content markers in {path}")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    path.write_text(before + start + "\n" + generated + "\n" + "          " + end + after)


def main():
    replace_between_markers(
        TRAINING_DYNAMICS_PAGE,
        generated_training_dynamics_papers(),
        PAPERS_START,
        PAPERS_END,
    )
    replace_between_markers(
        HOMEPAGE,
        generated_homepage_papers(),
        HOMEPAGE_PAPERS_START,
        HOMEPAGE_PAPERS_END,
    )


if __name__ == "__main__":
    main()
