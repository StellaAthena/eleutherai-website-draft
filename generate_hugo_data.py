#!/usr/bin/env python3
import csv
import json
import re
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
CONFERENCE_FAMILIES = (
    "NeurIPS",
    "ICML",
    "ICLR",
    "ACL",
    "EMNLP",
    "NAACL",
    "AACL",
    "COLM",
    "ECCV",
    "CIKM",
    "FAccT",
    "TACL",
    "TMLR",
)
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


def looks_like_workshop(value):
    text = (value or "").casefold()
    return "workshop" in text or "@" in text


def split_workshops(value):
    workshops = []
    raw_segments = re.split(r";|\n", value or "")
    for raw_segment in raw_segments:
        segment = raw_segment.strip()
        if not segment:
            continue
        comma_parts = [part.strip() for part in segment.split(",") if part.strip()]
        if len(comma_parts) > 1 and all(looks_like_workshop(part) for part in comma_parts):
            workshops.extend({"venue": part, "award_note": ""} for part in comma_parts)
            continue
        award_note = ""
        if len(comma_parts) > 1 and not looks_like_workshop(comma_parts[-1]):
            award_note = comma_parts[-1]
            segment = ", ".join(comma_parts[:-1]).strip()
        workshops.append({"venue": segment, "award_note": award_note})
    return workshops


def clean_award_text(value):
    value = (value or "").strip()
    value = re.sub(r"^workshop\s+", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^best paper runner-up$", "Best Paper Runner-up", value, flags=re.IGNORECASE)
    if value.casefold() == "best paper":
        return "Best Paper"
    return value[:1].upper() + value[1:] if value else ""


def clean_venue_label(venue, superlatives=None):
    venue = (venue or "").strip()
    for superlative in superlatives or []:
        venue = venue.replace(f" ({superlative})", "")
        if venue.endswith(f" {superlative}"):
            venue = venue[: -len(superlative)].rstrip()
    venue = re.sub(r",\s*best paper runner-up$", "", venue, flags=re.IGNORECASE)
    return venue.replace(" (Oral)", "").removesuffix(" Oral").strip()


def is_workshop_venue(venue):
    return looks_like_workshop(venue)


def venue_kind(venue):
    if venue == "arXiv":
        return "arxiv"
    if is_workshop_venue(venue):
        return "workshop"
    return "conference"


def venue_family(venue):
    venue = (venue or "").strip()
    if venue == "arXiv":
        return "arXiv"
    if "@" in venue:
        target = venue.rsplit("@", 1)[1].strip()
        target = re.sub(r"\b20\d{2}\b|\b\d{2}\b", "", target).strip()
        for family in CONFERENCE_FAMILIES:
            if family.casefold() in target.casefold():
                return family
        return target or venue
    if re.search(r"\bat\b", venue, flags=re.IGNORECASE) and is_workshop_venue(venue):
        target = re.split(r"\bat\b", venue, flags=re.IGNORECASE)[-1].strip()
        for family in CONFERENCE_FAMILIES:
            if family.casefold() in target.casefold():
                return family
    if is_workshop_venue(venue):
        for family in CONFERENCE_FAMILIES:
            if family.casefold() in venue.casefold():
                return family
    for family in CONFERENCE_FAMILIES:
        if venue.casefold().startswith(family.casefold()):
            return family
    return venue


def venue_track_label(venue, family, kind):
    label = re.sub(r"\s+", " ", (venue or "").strip())
    if kind == "arxiv":
        return "Preprints"
    if kind == "conference":
        if label == family:
            return "Main conference"
        label = re.sub(rf"^{re.escape(family)}\s*", "", label, flags=re.IGNORECASE).strip()
        label = re.sub(r"^\d{4}\s*", "", label).strip()
        return label or "Main conference"
    label = re.sub(rf"\s*@\s*{re.escape(family)}(\s*20\d{{2}}|\s*\d{{2}})?", "", label, flags=re.IGNORECASE).strip()
    label = re.sub(rf"\s+at\s+{re.escape(family)}(\s*20\d{{2}}|\s*\d{{2}})?", "", label, flags=re.IGNORECASE).strip()
    label = re.sub(rf"\s*\({re.escape(family)}\s*\d{{2,4}}\)", "", label, flags=re.IGNORECASE).strip()
    label = re.sub(rf"^{re.escape(family)}(\s*20\d{{2}}|\s*\d{{2}})?\s*", "", label, flags=re.IGNORECASE).strip()
    label = re.sub(r"\s+", " ", label)
    label = re.sub(r"\bworkshop\b", "Workshop", label, flags=re.IGNORECASE)
    compact = re.sub(r"[^a-z0-9]+", " ", label.casefold()).strip()
    if "mechinterp workshop" in compact or "mech interp workshop" in compact or "mechanistic interpretability workshop" in compact:
        return "MechInterp Workshop"
    return label or "Workshop"


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


def appearance_superlatives(row, raw_venue, kind, award_note="", has_separate_workshop=False):
    raw_lower = (raw_venue or "").casefold()
    award_lower = (award_note or "").casefold()
    selected = []
    for term in display_terms(row.get("Superlatives")):
        lower = term.casefold()
        if kind == "workshop":
            if "workshop" in lower or lower in raw_lower or ("best paper" in lower and "best paper" in award_lower):
                selected.append(clean_award_text(term))
        elif kind == "conference":
            if "workshop" in lower:
                continue
            if lower in raw_lower or not has_separate_workshop:
                selected.append(clean_award_text(term))
    if kind == "workshop" and award_note and "best paper" in award_lower:
        selected.append(clean_award_text(award_note))

    deduped = []
    seen = set()
    for term in selected:
        key = term.casefold()
        if term and key not in seen:
            seen.add(key)
            deduped.append(term)
    return deduped


def appearance_record(row, raw_venue, date, kind, award_note="", has_separate_workshop=False):
    venue = clean_venue_label(raw_venue, display_terms(row.get("Superlatives")))
    paper_date = pub_date(row)
    sort_date = date
    if kind == "workshop" and sort_date != datetime.min:
        sort_date = sort_date - timedelta(days=WORKSHOP_SORT_OFFSET_DAYS)
    if kind == "arxiv" and sort_date != datetime.min:
        sort_date = datetime(sort_date.year, 1, 1)
    return {
        "title": normalize_title(row.get("Title")),
        "url": clean_link(row.get("Link")),
        "date": display_year(paper_date),
        "date_sort": paper_date.strftime("%Y-%m-%d") if paper_date != datetime.min else "",
        "venue": venue,
        "venue_year": display_year(date),
        "kind": kind,
        "family": venue_family(venue),
        "group_sort_date": sort_date.strftime("%Y-%m-%d") if sort_date != datetime.min else "",
        "superlatives": appearance_superlatives(row, raw_venue, kind, award_note, has_separate_workshop),
    }


def paper_records(row):
    status = (row.get("Status") or "").strip().casefold()
    conference = (row.get("Conference or Journal") or "").strip()
    archival_date = parse_date(row.get("Archival Date"))
    workshops = split_workshops(row.get("Workshop"))
    workshop_date = parse_date(row.get("Workshop Date"))
    paper_date = pub_date(row)
    records = []

    if status == "accepted":
        separate_workshops = [
            workshop
            for workshop in workshops
            if clean_venue_label(workshop["venue"], display_terms(row.get("Superlatives"))) != clean_venue_label(conference, display_terms(row.get("Superlatives")))
        ]
        conference_is_real = conference and not conference.casefold().startswith("extended to")
        if conference_is_real:
            records.append(
                appearance_record(
                    row,
                    conference,
                    first_valid_date(archival_date, row_date(row), paper_date),
                    venue_kind(clean_venue_label(conference, display_terms(row.get("Superlatives")))),
                    has_separate_workshop=bool(separate_workshops),
                )
            )
        for workshop in separate_workshops or ([] if conference_is_real else workshops):
            records.append(
                appearance_record(
                    row,
                    workshop["venue"],
                    first_valid_date(workshop_date, row_date(row), paper_date),
                    "workshop",
                    award_note=workshop["award_note"],
                    has_separate_workshop=bool(separate_workshops),
                )
            )
        if not records:
            records.append(appearance_record(row, "arXiv", first_valid_date(paper_date, row_date(row)), "arxiv"))
        return records

    venue = homepage_venue(row)
    return [appearance_record(row, venue, venue_date(row, venue), venue_kind(venue))]


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
    records = []
    for row in selected:
        records.extend(paper_records(row))
    records.sort(key=lambda row: (row["group_sort_date"], row["date_sort"], row["title"]), reverse=True)
    return records


def library_paper_record(row):
    date = pub_date(row)
    venue = homepage_venue(row)
    if venue.casefold().startswith("extended to"):
        venue = (row.get("Workshop") or "").strip() or "arXiv"
    kind = venue_kind(venue)
    superlatives = []
    if kind in {"conference", "workshop"}:
        raw_venue = (row.get("Conference or Journal") or "").strip() if kind == "conference" else venue
        superlatives = appearance_superlatives(
            row,
            raw_venue,
            kind,
            has_separate_workshop=bool((row.get("Workshop") or "").strip() and kind == "conference"),
        )
    if kind == "conference":
        workshops = split_workshops(row.get("Workshop"))
        for term in display_terms(row.get("Superlatives")):
            if "workshop" not in term.casefold() or not workshops:
                continue
            award = clean_award_text(term).replace("Runner-up", "Runner Up")
            workshop = workshops[0]["venue"].replace("BioSafe Workshop", "BioSec Workshop")
            contextual = f"{award}, {workshop}"
            if contextual not in superlatives:
                superlatives.append(contextual)
    distinction_text = " ".join(superlatives).casefold()
    marker = ""
    if "runner" in distinction_text or "finalist" in distinction_text:
        marker = "runnerup"
    elif "best paper" in distinction_text:
        marker = "bestpaper"
    elif "spotlight" in distinction_text:
        marker = "spotlight"
    elif "oral" in distinction_text:
        marker = "oral"
    areas = []
    for field in ("Primary Area", "Additional Area"):
        area = (row.get(field) or "").strip()
        if area and area not in areas:
            areas.append(area)
    return {
        "title": normalize_title(row.get("Title")),
        "date": display_year(date),
        "date_sort": date.strftime("%Y-%m-%d") if date != datetime.min else "",
        "venue": venue,
        "family": venue_family(venue),
        "kind": kind,
        "status": (row.get("Status") or "").strip(),
        "areas": areas,
        "lead_org": (row.get("Lead Org") or "").strip(),
        "contact": (row.get("EleutherAI PoC") or "").strip(),
        "artifact_type": "Paper",
        "marker": marker,
        "superlatives": superlatives,
    }


def library_papers(rows):
    records = [
        library_paper_record(row)
        for row in rows
        if normalize_title(row.get("Title")) and pub_date(row) != datetime.min
    ]
    records.sort(key=lambda row: (row["date_sort"], row["title"]), reverse=True)
    return records


def grouped_papers(papers):
    groups = []
    by_key = {}
    for paper in papers:
        key = (paper["family"], paper["venue_year"])
        if key not in by_key:
            by_key[key] = {
                "family": paper["family"],
                "year": paper["venue_year"],
                "kind": paper["kind"],
                "label": f"{paper['family']}, {paper['venue_year']}" if paper["venue_year"] else paper["family"],
                "count": 0,
                "sort_date": paper["group_sort_date"],
                "venues": [],
                "_venue_map": {},
            }
            groups.append(by_key[key])
        group = by_key[key]
        label = venue_track_label(paper["venue"], paper["family"], paper["kind"])
        venue_key = (label.casefold(), paper["kind"])
        if venue_key not in group["_venue_map"]:
            group["_venue_map"][venue_key] = {
                "venue": paper["venue"],
                "label": label,
                "kind": paper["kind"],
                "count": 0,
                "sort_date": paper["group_sort_date"],
                "papers": [],
            }
            group["venues"].append(group["_venue_map"][venue_key])
        venue = group["_venue_map"][venue_key]
        venue["papers"].append(paper)
        venue["count"] += 1
        if paper["group_sort_date"] > venue["sort_date"]:
            venue["sort_date"] = paper["group_sort_date"]
        group["count"] += 1
        if paper["group_sort_date"] > group["sort_date"]:
            group["sort_date"] = paper["group_sort_date"]
        if group["kind"] == "arxiv" or paper["kind"] == "conference":
            group["kind"] = paper["kind"]
    groups.sort(key=lambda group: (group["sort_date"], group["label"]), reverse=True)
    for group in groups:
        group["venues"].sort(
            key=lambda venue: (
                {"conference": 2, "workshop": 1, "arxiv": 0}.get(venue["kind"], 0),
                venue["sort_date"],
                venue["label"],
            ),
            reverse=True,
        )
        for venue in group["venues"]:
            venue["papers"].sort(key=lambda paper: (paper["date_sort"], paper["title"]), reverse=True)
        group.pop("_venue_map")
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
    write_json("library_papers.json", library_papers(rows))
    print("Generated Hugo research data")


if __name__ == "__main__":
    main()
