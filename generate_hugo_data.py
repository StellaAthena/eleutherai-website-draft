#!/usr/bin/env python3
import csv
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent
PAPERS_CSV = ROOT / "eleutherai_papers_sheet_gid2053751678.csv"
AREA_PAPERS_CSV = ROOT / "research_area_papers.csv"
AREA_FILTERS_CSV = ROOT / "research_area_filters.csv"
OUTPUT_DIR = ROOT / "data" / "research"
HOMEPAGE_PAPER_LIMIT = 5


def parse_date(value):
    value = (value or "").strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return datetime.min


def display_full_date(date):
    if date == datetime.min:
        return ""
    return f"{date.day} {date.strftime('%B %Y')}"


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


def row_date(row):
    return parse_date(row.get("Sort Date") or row.get("Release Date") or row.get("Archival Date"))


def pub_date(row):
    return parse_date(row.get("Pub Date"))


def homepage_venue(row):
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


def display_venue(row, config):
    if config.get("display_venue"):
        return config["display_venue"]
    venue = (row.get("Conference or Journal") or row.get("Workshop") or row.get("Status") or "Paper").strip()
    if venue == "Accepted":
        return "Paper"
    return venue.replace(" (Oral)", " Oral")


def read_papers():
    with PAPERS_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
    date = pub_date(row)
    areas = []
    for key in ("Primary Area", "Additional Area"):
        value = (row.get(key) or "").strip()
        if value and value not in areas:
            areas.append(value)
    details = []
    if areas:
        details.append("Area: " + ", ".join(areas))
    if (row.get("Lead Org") or "").strip():
        details.append("Lead org: " + row["Lead Org"].strip())
    if (row.get("EleutherAI PoC") or "").strip():
        details.append("EleutherAI contact: " + row["EleutherAI PoC"].strip())
    return {
        "title": normalize_title(row.get("Title")),
        "url": clean_link(row.get("Link")),
        "date": display_full_date(date),
        "date_sort": date.strftime("%Y-%m-%d") if date != datetime.min else "",
        "venue": homepage_venue(row),
        "superlatives": display_terms(row.get("Superlatives")),
        "details": ". ".join(details) + ("." if details else ""),
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
        "date": display_full_date(date),
        "year": str(date.year) if date != datetime.min else "",
        "venue": venue,
        "superlatives": display_terms(row.get("Superlatives")),
        "sort_date": date.strftime("%Y-%m-%d") if date != datetime.min else "",
    }


def all_papers(rows):
    selected = [row for row in rows if normalize_title(row.get("Title")) and pub_date(row) != datetime.min]
    selected.sort(key=lambda row: (pub_date(row), normalize_title(row.get("Title"))), reverse=True)
    return [paper_record(row) for row in selected]


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
    rows = read_papers()
    papers = all_papers(rows)
    per_area = area_papers(rows)
    write_json("papers.json", papers)
    write_json("homepage_papers.json", papers[:HOMEPAGE_PAPER_LIMIT])
    write_json("area_papers.json", per_area)
    print("Generated Hugo research data")


if __name__ == "__main__":
    main()
