#!/usr/bin/env python3
import argparse
import csv
from html.parser import HTMLParser
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
PAPERS_CSV = ROOT / "eleutherai_papers.csv"
GENERATED_DIR = ROOT / "data" / "generated"
PAPER_URL_OVERRIDES = {
    "Position: Don't Just \"Fix it in Post'': A Science of AI Must Study Learning Dynamics": "https://arxiv.org/abs/2606.06533",
    "Automated Attribution Graph Interpretation via Probe Prompting": "https://arxiv.org/abs/2511.07002",
    "Faults in Our Formal Benchmarking: Dataset Defects and Evaluation Failures in Lean Theorem Proving": "https://arxiv.org/abs/2606.29493",
    "L1 Influence in L2 Language Models: A Human-centric Approach": "https://arxiv.org/abs/2606.14516",
    "Every Eval Ever: A Unifying Schema and Community Repository for AI Evaluation Results": "https://aclanthology.org/2026.cdl-1.15/",
    "Scaling Self-Supervised Representation Learning for Symbolic Piano Performance": "https://arxiv.org/abs/2506.23869",
    "Position: Write Code that People Want to Use": "https://openreview.net/forum?id=oH0XhgzJt0",
}
AREA_FILTERS_CSV = ROOT / "research_area_filters.csv"
OUTPUT_DIR = GENERATED_DIR / "research"
SCHOLAR_METRICS_PATH = GENERATED_DIR / "home_scholar_metrics.json"
HOME_GENERATED_METRICS_PATH = GENERATED_DIR / "home_generated_metrics.json"
BLOG_CONTENT_DIR = ROOT / "content-blog"
BLOG_POSTS_PATH = GENERATED_DIR / "blog_posts.json"
HOME_RECENT_OUTPUTS_PATH = GENERATED_DIR / "home_recent_outputs.json"
FRESHNESS_PATH = GENERATED_DIR / "freshness" / "research.json"
BLOG_BASE_URL = "https://blog.eleuther.ai"
HOME_RECENT_OUTPUT_LIMIT = 4
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
    "1LcB7_1lHZgO8_EmOkrvfV2BTaOngX95J5v8PJeuN4rM/export?format=csv"
)
SCHOLAR_PROFILE_URL = "https://scholar.google.com/citations?user=to2WKckAAAAJ&hl=en"
SCHOLAR_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
HF_ANALYTICS_URL = "https://huggingface.co/organizations/EleutherAI/settings/publisher/analytics?timePeriod=allTime"
HF_MODEL_DOWNLOADS_CACHE = GENERATED_DIR / "hf_model_downloads_cache.json"
REQUIRED_PAPER_HEADERS = {
    "Sort Date",
    "Title",
    "Display Authors",
    "Area",
    "Conference or Journal",
    "Workshop",
    "Superlative",
    "Link",
    "All Authors",
}


class ScholarStatsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_stats_table = False
        self.depth = 0
        self.cells = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table" and attrs.get("id") == "gsc_rsb_st":
            self.in_stats_table = True
            self.depth = 1
            return
        if self.in_stats_table:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.in_stats_table:
            self.depth -= 1
            if self.depth <= 0:
                self.in_stats_table = False

    def handle_data(self, data):
        if self.in_stats_table:
            text = " ".join(data.split())
            if text:
                self.cells.append(text)


def parse_date(value):
    value = (value or "").strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return datetime.min


def normalize_header(value):
    return " ".join((value or "").split()).casefold()


def header_value(row, name):
    normalized_name = normalize_header(name)
    for key, value in row.items():
        if normalize_header(key) == normalized_name:
            return value
    return ""


def highest_impact_header(headers):
    matches = [header for header in headers if normalize_header(header) == "highest impact"]
    return matches[0] if len(matches) == 1 else ""


def parse_highest_impact_marker(value):
    marker = normalize_header(str(value))
    if marker in {"", "false"}:
        return False
    if marker == "true":
        return True
    raise ValueError(f"unrecognized Highest Impact marker: {value!r}")


def parse_output_date(value):
    value = (value or "").strip()
    paper_date = parse_date(value)
    if paper_date != datetime.min:
        return paper_date
    value = re.sub(r"T(\d):", r"T0\1:", value)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def format_output_date(value):
    value = (value or "").strip()
    parsed = parse_date(value)
    if parsed == datetime.min:
        value = re.sub(r"T(\d):", r"T0\1:", value)
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return ""
    return parsed.strftime("%B %-d, %Y")


def display_year(date):
    if date == datetime.min:
        return ""
    return str(date.year)


def round_down(value, unit):
    return int(value / unit) * unit


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


def paper_identity_title(title):
    return re.sub(r"^Position:\s*", "", normalize_title(title), flags=re.IGNORECASE)


def split_terms(value):
    return [item.strip().casefold() for item in (value or "").split(";") if item.strip()]


def display_terms(value):
    return [item.strip() for item in (value or "").replace(",", ";").split(";") if item.strip()]


def full_author_terms(value):
    return [item.strip() for item in (value or "").split(";") if item.strip()]


def row_superlatives(row):
    # The current Sheet uses one Superlative cell whose text may contain commas.
    value = (row.get("Superlative") or "").strip()
    if value:
        return [value]
    return display_terms(row.get("Superlatives"))


def normalize_paper_row(row):
    normalized = dict(row)
    sort_date = (row.get("Sort Date") or "").strip()
    conference = (row.get("Conference or Journal") or "").strip()
    workshop = (row.get("Workshop") or "").strip()
    areas = [area.strip() for area in re.split(r"[;,]", row.get("Area") or "") if area.strip()]

    normalized["Pub Date"] = (row.get("Pub Date") or sort_date).strip()
    normalized["Archival Date"] = (row.get("Archival Date") or (sort_date if conference else "")).strip()
    normalized["Workshop Date"] = (row.get("Workshop Date") or (sort_date if workshop else "")).strip()
    normalized["Superlatives"] = (row.get("Superlatives") or row.get("Superlative") or "").strip()
    normalized["Primary Area"] = (row.get("Primary Area") or (areas[0] if areas else "")).strip()
    normalized["Additional Area"] = (
        row.get("Additional Area") or "; ".join(areas[1:])
    ).strip()
    normalized["all authors"] = (header_value(row, "all authors") or "").strip()
    normalized["Highest Impact"] = (header_value(row, "highest impact") or "").strip()
    if not (row.get("Status") or "").strip():
        normalized["Status"] = "Accepted" if conference or workshop else "Preprint"
    return normalized


def author_surname(name):
    name = " ".join((name or "").split())
    if not name:
        return ""
    if "," in name:
        return name.split(",", 1)[0].strip()
    parts = name.split()
    surname = parts[-1]
    particles = {"da", "de", "del", "der", "dos", "la", "le", "van", "von"}
    index = len(parts) - 2
    while index >= 0 and parts[index].casefold() in particles:
        surname = f"{parts[index]} {surname}"
        index -= 1
    return surname


def display_authors(authors, limit=4):
    surnames = [author_surname(author) for author in authors if author_surname(author)]
    if len(surnames) > limit:
        return ", ".join(surnames[:limit]) + ", et al."
    return ", ".join(surnames)


def author_search_terms(authors):
    terms = []
    for author in authors:
        author = " ".join((author or "").split())
        if not author:
            continue
        terms.append(author)
        if "," in author:
            surname, given = [part.strip() for part in author.split(",", 1)]
            if surname and given:
                terms.append(f"{given} {surname}")
    return terms


def paper_url(row):
    title = normalize_title(row.get("Title"))
    return clean_link(row.get("Link")) or PAPER_URL_OVERRIDES.get(title, "")


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
    return clean_venue_label(venue, row_superlatives(row))


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


def appearance_superlatives(row, raw_venue, kind, award_note="", has_separate_workshop=False):
    raw_lower = (raw_venue or "").casefold()
    award_lower = (award_note or "").casefold()
    selected = []
    for term in row_superlatives(row):
        lower = term.casefold()
        if kind == "workshop":
            if "workshop" in lower or lower in raw_lower or ("best paper" in lower and "best paper" in award_lower):
                selected.append(clean_award_text(term))
        elif kind == "conference":
            if "workshop" in lower:
                continue
            if lower in raw_lower or raw_lower in lower or not has_separate_workshop:
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
    venue = clean_venue_label(raw_venue, row_superlatives(row))
    paper_date = pub_date(row)
    sort_date = date
    if kind == "workshop" and sort_date != datetime.min:
        sort_date = sort_date - timedelta(days=WORKSHOP_SORT_OFFSET_DAYS)
    if kind == "arxiv" and sort_date != datetime.min:
        sort_date = datetime(sort_date.year, 1, 1)
    return {
        "title": normalize_title(row.get("Title")),
        "url": paper_url(row),
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
            if clean_venue_label(workshop["venue"], row_superlatives(row)) != clean_venue_label(conference, row_superlatives(row))
        ]
        conference_is_real = conference and not conference.casefold().startswith("extended to")
        if conference_is_real:
            records.append(
                appearance_record(
                    row,
                    conference,
                    first_valid_date(archival_date, row_date(row), paper_date),
                    venue_kind(clean_venue_label(conference, row_superlatives(row))),
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
        rows = [normalize_paper_row(row) for row in csv.DictReader(f)]
    missing_authors = [
        normalize_title(row.get("Title"))
        for row in rows
        if normalize_title(row.get("Title")) and not full_author_terms(row.get("all authors"))
    ]
    if missing_authors:
        raise SystemExit(
            "Papers CSV is missing `all authors` for: " + "; ".join(missing_authors)
        )
    return rows


def refresh_papers_csv(require_refresh=True):
    if not require_refresh:
        print("Using local papers CSV snapshot")
        return "offline"

    cache_buster = urlencode({"t": datetime.now().timestamp()})
    url = f"{PAPERS_SHEET_CSV_URL}&{cache_buster}"
    try:
        with urlopen(url, timeout=30) as response:
            text = response.read().decode("utf-8")
    except (OSError, URLError) as exc:
        raise SystemExit(f"Could not refresh Google Sheet CSV: {exc}") from exc

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    header = text.splitlines()[0] if text.splitlines() else ""
    headers = next(csv.reader([header]), [])
    if not REQUIRED_PAPER_HEADERS.issubset(set(headers)) or not highest_impact_header(headers):
        raise SystemExit("Google Sheet export did not look like the papers CSV.")

    PAPERS_CSV.write_text(text, encoding="utf-8")
    print("Refreshed papers CSV from Google Sheets")
    return "live"


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


def distinction_marker(superlatives):
    """Pick the single marker rendered by layouts/partials/paper-marker.html."""
    distinction_text = " ".join(superlatives).casefold()
    if "runner" in distinction_text or "finalist" in distinction_text:
        return "runnerup"
    if "best paper" in distinction_text or "outstanding" in distinction_text:
        return "bestpaper"
    if "spotlight" in distinction_text or "featured paper" in distinction_text:
        return "spotlight"
    if "oral" in distinction_text:
        return "oral"
    return ""


def area_paper_record(row, summary="", display_venue=""):
    date = pub_date(row)
    if date == datetime.min:
        date = row_date(row)
    venue = display_venue or homepage_venue(row)
    return {
        "title": normalize_title(row.get("Title")),
        "url": paper_url(row),
        "summary": summary,
        "date": display_year(date),
        "year": str(date.year) if date != datetime.min else "",
        "venue": venue,
        "authors": (row.get("Display Authors") or "").strip(),
        "marker": distinction_marker(row_superlatives(row)),
        "superlatives": row_superlatives(row),
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
        for term in row_superlatives(row):
            if "workshop" not in term.casefold() or not workshops:
                continue
            award = clean_award_text(term).replace("Runner-up", "Runner Up")
            if award not in superlatives:
                superlatives.append(award)
    marker = distinction_marker(superlatives)
    display_authors_text = (row.get("Display Authors") or "").strip()
    authors = full_author_terms(row.get("all authors"))
    areas = []
    for field in ("Primary Area", "Additional Area"):
        for area in (row.get(field) or "").split(";"):
            area = area.strip()
            if area and area not in areas:
                areas.append(area)
    return {
        "title": normalize_title(row.get("Title")),
        "url": paper_url(row),
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
        "authors": display_authors_text or display_authors(authors),
        "author_search": " ".join([display_authors_text, *author_search_terms(authors)]).strip(),
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


def row_areas(row):
    return set(split_terms(";".join([row.get("Primary Area") or "", row.get("Additional Area") or ""])))


def row_search_text(row):
    return " ".join(
        [
            normalize_title(row.get("Title")),
            "; ".join(row_superlatives(row)),
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
    records = {}
    for config in read_area_filters():
        records[config["key"]] = filtered_area_papers(rows, config)
    return records


def extract_scholar_citations(html):
    parser = ScholarStatsParser()
    parser.feed(html)
    cells = parser.cells
    for index, cell in enumerate(cells):
        if cell.casefold() != "citations":
            continue
        for candidate in cells[index + 1 : index + 3]:
            if re.fullmatch(r"[\d,]+", candidate):
                return int(candidate.replace(",", ""))
    raise ValueError("Could not find total citations in Google Scholar stats table.")


def fetch_scholar_citations():
    request = Request(
        SCHOLAR_PROFILE_URL,
        headers={
            "User-Agent": SCHOLAR_USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", "replace")
    return extract_scholar_citations(html)


def read_scholar_metric_cache():
    if not SCHOLAR_METRICS_PATH.exists():
        return None
    try:
        return json.loads(SCHOLAR_METRICS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def scholar_metric_payload(citations):
    rounded_citations = int(citations / 1000) * 1000
    return {
        "metrics": [
            {
                "value": f"{rounded_citations:,}",
                "label": "Citations",
                "url": SCHOLAR_PROFILE_URL,
            }
        ],
        "citations": citations,
        "rounded_citations": rounded_citations,
        "source_url": SCHOLAR_PROFILE_URL,
    }


def unavailable_scholar_metric_payload():
    return {
        "metrics": [],
        "citations": None,
        "source_url": SCHOLAR_PROFILE_URL,
    }


def write_scholar_metrics(offline=False):
    SCHOLAR_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if offline:
        cached = read_scholar_metric_cache()
        if cached and cached.get("metrics"):
            print("Using cached Google Scholar citation count")
            return cached, "offline"
        payload = unavailable_scholar_metric_payload()
        SCHOLAR_METRICS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print("No cached Google Scholar citation count available")
        return payload, "missing"

    try:
        citations = fetch_scholar_citations()
    except Exception as exc:
        cached = read_scholar_metric_cache()
        if cached and cached.get("metrics"):
            print("Google Scholar refresh failed; using cached citation count")
            return cached, "cache"
        payload = unavailable_scholar_metric_payload()
        SCHOLAR_METRICS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print("Google Scholar refresh failed; citation metric omitted")
        return payload, "missing"

    payload = scholar_metric_payload(citations)
    SCHOLAR_METRICS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Refreshed Google Scholar citation count")
    return payload, "live"


def fetch_hf_model_downloads():
    env_value = os.environ.get("HF_MODEL_DOWNLOADS")
    if env_value:
        return env_value

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ValueError("Playwright not installed")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(HF_ANALYTICS_URL, timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)

            text = page.inner_text("body")
            match = re.search(r'Models\s*\(\d+\)\s*(\d+(?:\.\d+)?M)', text)

            if not match:
                match = re.search(r'(\d+M)\s+downloads', text)

            browser.close()

            if match:
                return match.group(1)
            else:
                raise ValueError("Could not find model download count in rendered HF analytics page")
    except Exception as exc:
        raise ValueError(f"HuggingFace fetch failed: {exc}") from exc


def read_hf_downloads_cache():
    if not HF_MODEL_DOWNLOADS_CACHE.exists():
        return None
    try:
        return json.loads(HF_MODEL_DOWNLOADS_CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_hf_downloads_cache(value):
    HF_MODEL_DOWNLOADS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    HF_MODEL_DOWNLOADS_CACHE.write_text(json.dumps({"value": value}, indent=2) + "\n", encoding="utf-8")


def hf_model_downloads_payload(offline=False):
    if offline:
        cached = read_hf_downloads_cache()
        if cached and cached.get("value"):
            print("Using cached HuggingFace model download count")
            return cached["value"], "offline"
        print("No cached HuggingFace model download count available")
        return "", "missing"

    try:
        value = fetch_hf_model_downloads()
        write_hf_downloads_cache(value)
        print("Refreshed HuggingFace model download count")
        status = "provided" if os.environ.get("HF_MODEL_DOWNLOADS") else "live"
        return value, status
    except SystemExit:
        raise
    except Exception as exc:
        cached = read_hf_downloads_cache()
        if cached and cached.get("value"):
            print(f"HuggingFace fetch failed ({exc}); using cached model download count")
            return cached["value"], "cache"
        print(f"HuggingFace fetch failed ({exc}); model download metric omitted")
        print("To enable HF downloads fetching, install playwright: pip install playwright")
        return "", "missing"


def write_freshness_report(mode, sources):
    FRESHNESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "sources": sources,
    }
    FRESHNESS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def require_fresh_sources(sources):
    allowed = {"live", "provided", "local"}
    stale = [name for name, details in sources.items() if details["status"] not in allowed]
    if stale:
        raise SystemExit("Strict live verification failed for: " + ", ".join(stale))


def publication_metric_payload(rows):
    titles = {
        normalize_title(row.get("Title"))
        for row in rows
        if normalize_title(row.get("Title")) and pub_date(row) != datetime.min
    }
    count = len(titles)
    rounded_count = round_down(count, 10)
    return {
        "value": f"{rounded_count:,}+",
        "label": "Publications",
        "count": count,
        "rounded_count": rounded_count,
        "source": "papers_sheet_sort_date",
        "rounded_to": 10,
    }


def write_home_generated_metrics(rows, scholar_payload, hf_downloads, offline=False):
    metrics = {
        "publication_count": publication_metric_payload(rows),
    }
    if scholar_payload.get("metrics"):
        metric = scholar_payload["metrics"][0]
        value = metric["value"]
        if not value.endswith("+"):
            value = value + "+"
        metrics["scholar_citations"] = {
            "value": value,
            "label": metric["label"],
            "url": metric.get("url", ""),
            "count": scholar_payload.get("citations"),
            "rounded_count": scholar_payload.get("rounded_citations"),
            "source": scholar_payload.get("source_url", ""),
            "rounded_to": 1000,
        }
    if hf_downloads:
        hf_value = hf_downloads if hf_downloads.endswith("+") else hf_downloads + "+"
        metrics["model_downloads"] = {
            "value": hf_value,
            "label": "Model Downloads",
            "url": "https://huggingface.co/EleutherAI",
            "source": HF_ANALYTICS_URL,
        }
    payload = {"metrics": metrics}
    HOME_GENERATED_METRICS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_json(name, data):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_front_matter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not match:
        return {}
    values = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator or key not in {"title", "date", "draft", "url"}:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def write_blog_posts():
    posts = []
    for path in BLOG_CONTENT_DIR.rglob("*.md"):
        if path.name == "_index.md":
            continue
        front_matter = read_front_matter(path)
        if front_matter.get("draft", "").casefold() == "true":
            continue
        title = front_matter.get("title", "").strip()
        date = front_matter.get("date", "").strip()
        if not title or not date:
            continue
        relative = path.relative_to(BLOG_CONTENT_DIR)
        slug = relative.parent.name if path.name == "index.md" else path.stem
        posts.append(
            {
                "title": title,
                "date": date,
                "url": f"{BLOG_BASE_URL}/{slug.lower()}/",
            }
        )
    posts.sort(key=lambda post: (post["date"], post["title"]), reverse=True)
    BLOG_POSTS_PATH.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return posts


def recent_outputs(rows, blog_posts, limit=HOME_RECENT_OUTPUT_LIMIT):
    outputs = []
    invalid_markers = []
    for row in rows:
        marker = row.get("Highest Impact", header_value(row, "highest impact"))
        try:
            selected = parse_highest_impact_marker(marker)
        except ValueError:
            invalid_markers.append(f"{normalize_title(row.get('Title'))}: {marker!r}")
            continue
        if not selected:
            continue
        title = normalize_title(row.get("Title"))
        date_value = (row.get("Sort Date") or "").strip()
        date = parse_output_date(date_value)
        url = paper_url(row)
        if not title or date == datetime.min or not url:
            raise ValueError(f"Highest Impact paper is missing a title, Sort Date, or link: {title or '<untitled>'}")
        venue = homepage_venue(row)
        display_date = format_output_date(date_value)
        meta = f"{venue} · {display_date}" if venue else display_date
        outputs.append(
            {
                "kind": "Paper",
                "title": title,
                "url": url,
                "date": date.strftime("%Y-%m-%dT%H:%M:%S"),
                "meta": meta,
            }
        )

    if invalid_markers:
        raise ValueError("Invalid Highest Impact markers: " + "; ".join(invalid_markers))

    # Blog posts already appear in the homepage Latest panel, so this list is papers only.

    unique_outputs = {}
    for output in outputs:
        key = (output["kind"].casefold(), output["url"], output["title"].casefold())
        unique_outputs[key] = output
    sorted_outputs = sorted(
        unique_outputs.values(),
        key=lambda output: (output["date"], output["title"], output["kind"]),
        reverse=True,
    )
    return sorted_outputs[:limit]


def write_home_recent_outputs(rows, blog_posts):
    outputs = recent_outputs(rows, blog_posts)
    HOME_RECENT_OUTPUTS_PATH.write_text(
        json.dumps(outputs, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description="Generate Hugo data from authoritative sources.")
    parser.add_argument("--offline", action="store_true", help="use checked-in external-data snapshots")
    parser.add_argument("--strict", action="store_true", help="fail if a live external source uses a fallback")
    args = parser.parse_args()
    if args.offline and args.strict:
        parser.error("--offline and --strict cannot be used together")

    papers_status = refresh_papers_csv(require_refresh=not args.offline)
    rows = read_papers()
    scholar_payload, scholar_status = write_scholar_metrics(offline=args.offline)
    hf_downloads, hf_status = hf_model_downloads_payload(offline=args.offline)
    write_home_generated_metrics(rows, scholar_payload, hf_downloads, offline=args.offline)
    papers = all_papers(rows)
    per_area = area_papers(rows)
    write_json("papers.json", papers)
    write_json("homepage_papers.json", papers[:HOMEPAGE_PAPER_LIMIT])
    write_json("paper_groups.json", grouped_papers(papers))
    write_json("homepage_paper_groups.json", grouped_papers(papers[:HOMEPAGE_GROUPED_PAPER_LIMIT]))
    write_json("area_papers.json", per_area)
    write_json("library_papers.json", library_papers(rows))
    blog_posts = write_blog_posts()
    with PAPERS_CSV.open(newline="", encoding="utf-8") as papers_file:
        local_headers = next(csv.reader(papers_file), [])
    if not args.offline or highest_impact_header(local_headers):
        write_home_recent_outputs(rows, blog_posts)
    elif not HOME_RECENT_OUTPUTS_PATH.exists():
        raise SystemExit("Offline papers CSV has no Highest Impact column or generated homepage output snapshot.")
    else:
        print("Using generated homepage output snapshot")
    sources = {
        "google_sheet": {"status": papers_status, "url": PAPERS_SHEET_CSV_URL},
        "google_scholar": {"status": scholar_status, "url": SCHOLAR_PROFILE_URL},
        "huggingface_downloads": {"status": hf_status, "url": HF_ANALYTICS_URL},
        "blog_content": {"status": "local", "path": str(BLOG_CONTENT_DIR.relative_to(ROOT))},
    }
    write_freshness_report("offline" if args.offline else "live", sources)
    if args.strict:
        require_fresh_sources(sources)
    print("Generated Hugo research data")


if __name__ == "__main__":
    main()
