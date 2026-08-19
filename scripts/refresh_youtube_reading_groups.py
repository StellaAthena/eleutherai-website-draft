#!/usr/bin/env python3
"""Refresh the Community page's recent reading-group recordings."""

import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


CHANNEL_ID = "UCljbpGFxy_7i4bMDXyuB96A"
CHANNEL_URL = "https://www.youtube.com/@Eleuther_AI"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "community_reading_groups.json"
VIDEO_LIMIT = 3
READING_GROUP_PATTERN = re.compile(r"\b(?:reading\s+group|rg)\b", re.IGNORECASE)
NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}
OVERVIEW_OVERRIDES = {
    "e12wdaW2xgk": "A discussion of cross-datacenter LLM serving that separates prefill and decode work by transferring KV caches between independently scaled clusters."
}


def display_date(value):
    published = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return f"{published.strftime('%B')} {published.day}, {published.year}"


def presentation_fields(title, description, video_id):
    reading_group = "EleutherAI Reading Group"
    session_title = title

    full_name_match = re.match(
        r"^(?P<group>.+?)\s+Reading Group(?:\s+Session\s+\d+)?:\s*(?P<session>.+)$",
        title,
        re.IGNORECASE,
    )
    abbreviation_match = re.match(
        r"^(?P<group>.+?)\s+RG,.*?\s+Session:\s*(?P<session>.+)$",
        title,
        re.IGNORECASE,
    )
    match = full_name_match or abbreviation_match
    if match:
        reading_group = f"{match.group('group').strip()} Reading Group"
        session_title = match.group("session").strip()

    overview = OVERVIEW_OVERRIDES.get(video_id)
    if not overview:
        paragraphs = [re.sub(r"\s+", " ", paragraph).strip() for paragraph in description.split("\n\n")]
        substantive = next(
            (
                paragraph
                for paragraph in paragraphs
                if paragraph
                and not paragraph.lower().endswith("meeting recording.")
                and not paragraph.lower().startswith(("paper:", "slides:", "presenter:", "links:", "reading group on discord:"))
            ),
            "",
        )
        sentence_match = re.match(r"^.*?[.!?](?:\s|$)", substantive)
        overview = sentence_match.group(0).strip() if sentence_match else substantive
    if not overview:
        overview = f"A technical discussion of {session_title}."

    return session_title, reading_group, overview


def parse_feed(payload):
    root = ET.fromstring(payload)
    recordings = []
    for entry in root.findall("atom:entry", NAMESPACES):
        title = entry.findtext("atom:title", default="", namespaces=NAMESPACES).strip()
        if not READING_GROUP_PATTERN.search(title):
            continue

        video_id = entry.findtext("yt:videoId", default="", namespaces=NAMESPACES).strip()
        published = entry.findtext("atom:published", default="", namespaces=NAMESPACES).strip()
        description = entry.findtext("media:group/media:description", default="", namespaces=NAMESPACES).strip()
        if not video_id or not published:
            continue

        session_title, reading_group, overview = presentation_fields(title, description, video_id)

        recordings.append(
            {
                "title": title,
                "session_title": session_title,
                "reading_group": reading_group,
                "overview": overview,
                "published": published,
                "date": display_date(published),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "video_id": video_id,
            }
        )

    recordings.sort(key=lambda recording: recording["published"], reverse=True)
    return recordings[:VIDEO_LIMIT]


def validate_recordings(recordings):
    if len(recordings) != VIDEO_LIMIT:
        raise ValueError(f"expected {VIDEO_LIMIT} reading-group recordings, found {len(recordings)}")
    for recording in recordings:
        missing = {
            "title",
            "session_title",
            "reading_group",
            "overview",
            "published",
            "date",
            "url",
            "video_id",
        } - recording.keys()
        if missing:
            raise ValueError(f"recording is missing fields: {', '.join(sorted(missing))}")


def read_cache():
    data = json.loads(OUTPUT_PATH.read_text())
    validate_recordings(data["recordings"])
    return data


def fetch_feed():
    request = urllib.request.Request(FEED_URL, headers={"User-Agent": "EleutherAI website build"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def write_cache(recordings):
    data = {"channel_url": CHANNEL_URL, "feed_url": FEED_URL, "recordings": recordings}
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="validate and retain the checked-in snapshot")
    args = parser.parse_args()

    if args.offline:
        data = read_cache()
        print(f"Using {len(data['recordings'])} cached YouTube reading-group recordings.")
        return

    try:
        recordings = parse_feed(fetch_feed())
        validate_recordings(recordings)
        write_cache(recordings)
        print(f"Refreshed {len(recordings)} YouTube reading-group recordings.")
    except Exception as error:
        try:
            data = read_cache()
        except Exception:
            raise RuntimeError(f"YouTube refresh failed and no valid cache is available: {error}") from error
        print(
            f"Warning: YouTube refresh failed ({error}); using {len(data['recordings'])} cached recordings.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
