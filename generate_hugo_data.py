#!/usr/bin/env python3
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
PAPERS_CSV = ROOT / "eleutherai_papers_sheet_gid2053751678.csv"
AREA_PAPERS_CSV = ROOT / "research_area_papers.csv"
AREA_FILTERS_CSV = ROOT / "research_area_filters.csv"
OUTPUT_DIR = ROOT / "data" / "research"
HOMEPAGE_PAPER_LIMIT = 10
HOMEPAGE_GROUPED_PAPER_LIMIT = 30
WORKSHOP_SORT_OFFSET_DAYS = 7
PAPERS_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "14amb2CM9nVQR_-ZqpGuNPSSdMxsAk0YEoAvetgEyGRw/export?format=csv&gid=2053751678"
)


def parse_date(value):
    value = (value or "").strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return datetime.min


def display_year(date):
    if date == datetime.min:
        return ""
    return str(date.year)


def first_valid_date(*dates):
    for date in dates:
        if date != datetime.min:
            return date
    return datetime.min


def clean_link(link):
    link = (link or "").strip()
    if not link:
        return ""
    parts = urlsplit(link)
    if parts.netloc == "openreview.net":
        query = parts.query.split("&referrer=", 1)[0]
        return urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))
    return link


def normalize_title(title):
    return " ".join((title or "").split())


def split_terms(value):
    return [item.strip().casefold() for item in (value or "").split(";") if item.strip()]


def display_terms(value):
    return [item.strip() for item in (value or "").replace(",", ";").split(";") if item.strip()]


def clean_venue_label(venue, superlatives=None):
    venue = (venue or "").strip()
    for superlative in superlatives or []:
        venue = venue.replace(f" ({superlative})", "")
        if venue.endswith(f" {superlative}"):
            venue = venue[: -len(superlative)].rstrip()
    return venue.replace(" (Oral)", "").removesuffix(" Oral").strip()


def is_workshop_venue(venue):
    text = (venue or "").casefold()
    return "workshop" in text or "@" in text


def venue_kind(venue):
    if venue == "arXiv":
        return "arxiv"
    if is_workshop_venue(venue):
        return "workshop"
    return "conference"


def row_date(row):
    return first_valid_date(
        parse_date(row.get("Sort Date")),
        parse_date(row.get("Release Date")),
        parse_date(row.get("Archival Date")),
    )


def pub_date(row):
    return parse_date(row.get("Pub Date"))


def homepage_venue(row):
    status = (row.get("Status") or "").strip().casefold()
    conference = (row.get("Conference or Journal") or "").strip()
    workshop = (row.get("Workshop") or "").strip()
    if status == "accepted":
        venue = conference or workshop or "arXiv"
    elif conference:
        # Under-review conference papers should show their prior public venue.
        venue = workshop or "arXiv"
    else:
        venue = "arXiv"
    return clean_venue_label(venue, display_terms(row.get("Superlatives")))


def venue_date(row, venue):
    if venue == "arXiv":
        return first_valid_date(pub_date(row), row_date(row))
    if is_workshop_venue(venue):
        return first_valid_date(parse_date(row.get("Workshop Date")), row_date(row), pub_date(row))
    return first_valid_date(parse_date(row.get("Archival Date")), row_date(row), pub_date(row))


def group_sort_date(row, venue):
    date = venue_date(row, venue)
    if date == datetime.min:
        return date
    if venue == "arXiv":
        return datetime(date.year, 1, 1)
    if is_workshop_venue(venue):
        return date - timedelta(days=WORKSHOP_SORT_OFFSET_DAYS)
    return date


def display_venue(row, config):
    if config.get("display_venue"):
        return config["display_venue"]
    venue = (row.get("Conference or Journal") or row.get("Workshop") or row.get("Status") or "Paper").strip()
    if venue == "Accepted":
        return "Paper"
    return clean_venue_label(venue, display_terms(row.get("Superlatives")))


def read_papers():
    with PAPERS_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def refresh_papers_csv(require_refresh=True):
    if not require_refresh:
        print("Using local papers CSV snapshot")
        return

    cache_buster = urlencode({"t": datetime.now().timestamp()})
    url = f"{PAPERS_SHEET_CSV_URL}&{cache_buster}"
    try:
        with urlopen(url, timeout=30) as response:
            text = response.read().decode("utf-8")
    except (OSError, URLError) as exc:
        raise SystemExit(f"Could not refresh Google Sheet CSV: {exc}") from exc

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    header = text.splitlines()[0] if text.splitlines() else ""
    if "Sort Date" not in header or "Title" not in header:
        raise SystemExit("Google Sheet export did not look like the papers CSV.")

    PAPERS_CSV.write_text(text, encoding="utf-8")
    print("Refreshed papers CSV from Google Sheets")


def read_area_configs(area):
    with AREA_PAPERS_CSV.open(newline="", encoding="utf-8") as f:
        return [
            {
                "title": row["Title"],
                "summary": row["Summary"],
                "display_venue": row.get("Display Venue", "").strip(),
            }
            for row in csv.DictReader(f)
            if row.get("Research Area") == area
        ]


def read_area_filters():
    with AREA_FILTERS_CSV.open(newline="", encoding="utf-8") as f:
        return [
            {
                "key": row["Area Key"].strip(),
                "broad_areas": split_terms(row.get("Broad Areas")),
                "include_terms": split_terms(row.get("Include Terms")),
                "exclude_terms": split_terms(row.get("Exclude Terms")),
            }
            for row in csv.DictReader(f)
            if row.get("Area Key", "").strip()
        ]


def paper_record(row):
    paper_date = pub_date(row)
    venue = homepage_venue(row)
    event_date = venue_date(row, venue)
    sort_date = group_sort_date(row, venue)
    return {
        "title": normalize_title(row.get("Title")),
        "url": clean_link(row.get("Link")),
        "date": display_year(paper_date),
        "date_sort": paper_date.strftime("%Y-%m-%d") if paper_date != datetime.min else "",
        "venue": venue,
        "venue_year": display_year(event_date),
        "group_sort_date": sort_date.strftime("%Y-%m-%d") if sort_date != datetime.min else "",
        "superlatives": display_terms(row.get("Superlatives")),
    }


def area_paper_record(row, summary="", display_venue=""):
    date = pub_date(row)
    if date == datetime.min:
        date = row_date(row)
    venue = display_venue or homepage_venue(row)
    return {
        "title": normalize_title(row.get("Title")),
        "url": clean_link(row.get("Link")),
        "summary": summary,
        "date": display_year(date),
        "year": str(date.year) if date != datetime.min else "",
        "venue": venue,
        "superlatives": display_terms(row.get("Superlatives")),
        "sort_date": date.strftime("%Y-%m-%d") if date != datetime.min else "",
    }


def all_papers(rows):
    selected = [row for row in rows if normalize_title(row.get("Title")) and pub_date(row) != datetime.min]
    records = [paper_record(row) for row in selected]
    records.sort(key=lambda row: (row["group_sort_date"], row["date_sort"], row["title"]), reverse=True)
    return records


def grouped_papers(papers):
    groups = []
    by_key = {}
    for paper in papers:
        key = (paper["venue"], paper["venue_year"])
        if key not in by_key:
            by_key[key] = {
                "venue": paper["venue"],
                "year": paper["venue_year"],
                "kind": venue_kind(paper["venue"]),
                "label": f"{paper['venue']}, {paper['venue_year']}" if paper["venue_year"] else paper["venue"],
                "count": 0,
                "sort_date": paper["group_sort_date"],
                "papers": [],
            }
            groups.append(by_key[key])
        group = by_key[key]
        group["papers"].append(paper)
        group["count"] += 1
        if paper["group_sort_date"] > group["sort_date"]:
            group["sort_date"] = paper["group_sort_date"]
    groups.sort(key=lambda group: (group["sort_date"], group["label"]), reverse=True)
    for group in groups:
        group["papers"].sort(key=lambda paper: (paper["date_sort"], paper["title"]), reverse=True)
    return groups


def configured_area_papers(rows, area):
    configs = read_area_configs(area)
    by_title = {normalize_title(row.get("Title")): row for row in rows}
    records = []
    for config in configs:
        row = by_title.get(normalize_title(config["title"]))
        if not row:
            raise SystemExit(f"Missing configured paper title in papers CSV: {config['title']}")
        records.append(area_paper_record(row, config["summary"], display_venue(row, config)))
    records.sort(key=lambda row: (row["sort_date"], row["title"]), reverse=True)
    return records


def row_areas(row):
    return {
        (row.get("Primary Area") or "").strip().casefold(),
        (row.get("Additional Area") or "").strip().casefold(),
    }


def row_search_text(row):
    return " ".join(
        [
            normalize_title(row.get("Title")),
            row.get("Superlatives") or "",
            row.get("Conference or Journal") or "",
            row.get("Workshop") or "",
        ]
    ).casefold()


def matches_area_filter(row, config):
    areas = row_areas(row)
    if config["broad_areas"] and not areas.intersection(config["broad_areas"]):
        return False
    text = row_search_text(row)
    if config["include_terms"] and not any(term in text for term in config["include_terms"]):
        return False
    if config["exclude_terms"] and any(term in text for term in config["exclude_terms"]):
        return False
    return pub_date(row) != datetime.min or row_date(row) != datetime.min


def filtered_area_papers(rows, config):
    records = [area_paper_record(row) for row in rows if matches_area_filter(row, config)]
    records.sort(key=lambda row: (row["sort_date"], row["title"]), reverse=True)
    return records


def area_papers(rows):
    records = {
        "training_dynamics": configured_area_papers(rows, "Training Dynamics"),
    }
    for config in read_area_filters():
        records[config["key"]] = filtered_area_papers(rows, config)
    return records


def write_json(name, data):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    offline = "--offline" in sys.argv[1:]
    refresh_papers_csv(require_refresh=not offline)
    rows = read_papers()
    papers = all_papers(rows)
    per_area = area_papers(rows)
    write_json("papers.json", papers)
    write_json("homepage_papers.json", papers[:HOMEPAGE_PAPER_LIMIT])
    write_json("paper_groups.json", grouped_papers(papers))
    write_json("homepage_paper_groups.json", grouped_papers(papers[:HOMEPAGE_GROUPED_PAPER_LIMIT]))
    write_json("area_papers.json", per_area)
    print("Generated Hugo research data")


if __name__ == "__main__":
    main()
