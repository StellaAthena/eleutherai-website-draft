#!/usr/bin/env python3
"""Refresh the Community page's reading-group cards from YouTube playlists.

Each reading group in data/reading_groups.yaml is a series (playlist) on the
EleutherAI channel. The card is titled with the series name and links to the
newest recording in that playlist. Groups without a playlist ID fall back to
matching the newest channel upload whose title matches `title_pattern`.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import yaml


CHANNEL_ID = "UCljbpGFxy_7i4bMDXyuB96A"
CHANNEL_URL = "https://www.youtube.com/@Eleuther_AI"
PLAYLISTS_URL = f"{CHANNEL_URL}/playlists"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
PLAYLIST_FEED_URL = "https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
UPLOADS_PLAYLIST_ID = "UU" + CHANNEL_ID[2:]
API_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "reading_groups.yaml"
OUTPUT_PATH = ROOT / "data" / "generated" / "community_reading_groups.json"
FRESHNESS_PATH = ROOT / "data" / "generated" / "freshness" / "youtube.json"
GROUP_LIMIT = 6
NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}
OVERVIEW_OVERRIDES = {
    "e12wdaW2xgk": "A discussion of cross-datacenter LLM serving that separates prefill and decode work by transferring KV caches between independently scaled clusters."
}
REQUIRED_FIELDS = {
    "name",
    "playlist_id",
    "playlist_url",
    "url",
    "latest_title",
    "latest_session_title",
    "video_id",
    "published",
    "date",
    "overview",
    "source",
}


def display_date(value):
    published = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return f"{published.strftime('%B')} {published.day}, {published.year}"


SESSION_TITLE_PATTERNS = [
    # "Planning, Reasoning, and Agents RG, 2026-03-11 Session: Reasoning about ..."
    re.compile(r"^(?P<group>.+?)\s+RG,.*?\bSession:\s*(?P<session>.+)$", re.IGNORECASE),
    # "ML Performance Reading Group Session 25: Prefill as a Service"
    # "MoE Reading Group #7 - Hash Layers for Large Sparse Models"
    # "Math Reading Group - Random Matrix Theory II Wishart Matrices"
    re.compile(
        r"^(?P<group>.+?\bReading Group)\b\s*(?:Session\s*#?\d+|#\d+)?\s*[:\-\u2013\u2014]\s*(?P<session>.+)$",
        re.IGNORECASE,
    ),
]
TRAILING_DATE_PATTERN = re.compile(r"\s*\(\d{1,2}/\d{1,2}/\d{2,4}\)\s*$")


def session_title(title):
    """Strip the series prefix from an upload title, leaving the session's own title."""
    session = title
    for pattern in SESSION_TITLE_PATTERNS:
        match = pattern.match(title)
        if match:
            session = match.group("session").strip()
            break
    return TRAILING_DATE_PATTERN.sub("", session).strip() or title


def overview_text(description, video_id, fallback_title):
    overview = OVERVIEW_OVERRIDES.get(video_id)
    if overview:
        return overview
    paragraphs = [re.sub(r"\s+", " ", paragraph).strip() for paragraph in (description or "").split("\n\n")]
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
    # Skip descriptions that merely restate the upload title; the card shows the title already.
    if overview.casefold().rstrip(".") == fallback_title.casefold().rstrip("."):
        return ""
    return overview


def load_config(path=CONFIG_PATH):
    data = yaml.safe_load(path.read_text()) or {}
    groups = []
    for entry in data.get("groups", []):
        name = (entry.get("name") or "").strip()
        if not name:
            raise ValueError("every reading group needs a name")
        groups.append(
            {
                "name": name,
                "playlist_id": (entry.get("playlist_id") or "").strip(),
                "title_pattern": (entry.get("title_pattern") or "").strip(),
            }
        )
    if not groups:
        raise ValueError(f"no reading groups configured in {path}")
    return groups[:GROUP_LIMIT]


def parse_feed_videos(payload):
    """Return every video in an Atom feed (channel or playlist), newest first."""
    root = ET.fromstring(payload)
    videos = []
    for entry in root.findall("atom:entry", NAMESPACES):
        video_id = entry.findtext("yt:videoId", default="", namespaces=NAMESPACES).strip()
        published = entry.findtext("atom:published", default="", namespaces=NAMESPACES).strip()
        if not video_id or not published:
            continue
        videos.append(
            {
                "video_id": video_id,
                "title": entry.findtext("atom:title", default="", namespaces=NAMESPACES).strip(),
                "description": entry.findtext("media:group/media:description", default="", namespaces=NAMESPACES).strip(),
                "published": published,
            }
        )
    videos.sort(key=lambda video: video["published"], reverse=True)
    return videos


def parse_api_videos(payload):
    data = json.loads(payload)
    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        video_id = snippet.get("resourceId", {}).get("videoId", "").strip()
        published = (
            item.get("contentDetails", {}).get("videoPublishedAt", "").strip()
            or snippet.get("publishedAt", "").strip()
        )
        if not video_id or not published:
            continue
        videos.append(
            {
                "video_id": video_id,
                "title": snippet.get("title", "").strip(),
                "description": snippet.get("description", "").strip(),
                "published": published,
            }
        )
    return videos, data.get("nextPageToken", "")


def group_record(group, video, source):
    playlist_id = group["playlist_id"]
    if playlist_id:
        url = f"https://www.youtube.com/watch?v={video['video_id']}&list={playlist_id}"
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    else:
        url = f"https://www.youtube.com/watch?v={video['video_id']}"
        playlist_url = ""
    title = video["title"]
    return {
        "name": group["name"],
        "playlist_id": playlist_id,
        "playlist_url": playlist_url,
        "url": url,
        "latest_title": title,
        "latest_session_title": session_title(title),
        "video_id": video["video_id"],
        "published": video["published"],
        "date": display_date(video["published"]),
        "overview": overview_text(video.get("description", ""), video["video_id"], session_title(title)),
        "source": source,
    }


def select_latest(videos, pattern=""):
    if pattern:
        matcher = re.compile(pattern, re.IGNORECASE)
        videos = [video for video in videos if matcher.search(video["title"])]
    return videos[0] if videos else None


def build_records(groups, playlist_videos, channel_videos):
    """Assemble one card per configured group from already-fetched video lists.

    Groups whose playlist yields nothing are skipped with a warning so one empty
    or misconfigured series does not block the others.
    """
    records = []
    skipped = []
    for group in groups:
        if group["playlist_id"]:
            video = select_latest(playlist_videos.get(group["playlist_id"], []))
            source = "playlist"
        elif group["title_pattern"]:
            video = select_latest(channel_videos, group["title_pattern"])
            source = "channel_feed"
        else:
            raise ValueError(f"{group['name']}: set playlist_id or title_pattern")
        if not video:
            skipped.append(group["name"])
            continue
        records.append(group_record(group, video, source))
    records.sort(key=lambda record: record["published"], reverse=True)
    if skipped:
        print(
            "No recordings found for: " + ", ".join(skipped)
            + ". Check that each playlist is public and its ID matches the `list=` value in the playlist URL.",
            file=sys.stderr,
        )
    if not records:
        raise ValueError("no reading group produced a recording")
    return records


def validate_records(records):
    if not records:
        raise ValueError("expected at least one reading-group card")
    if len(records) > GROUP_LIMIT:
        raise ValueError(f"expected at most {GROUP_LIMIT} reading-group cards, found {len(records)}")
    for record in records:
        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            raise ValueError(f"reading group is missing fields: {', '.join(sorted(missing))}")


def read_cache():
    data = json.loads(OUTPUT_PATH.read_text())
    validate_records(data["groups"])
    return data


def fetch_url(url):
    request = urllib.request.Request(url, headers={"User-Agent": "EleutherAI website build"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def fetch_api_playlist(playlist_id, api_key, pages=20):
    videos = []
    page_token = ""
    for _ in range(pages):
        params = {"part": "snippet,contentDetails", "playlistId": playlist_id, "maxResults": 50, "key": api_key}
        if page_token:
            params["pageToken"] = page_token
        page_videos, page_token = parse_api_videos(fetch_url(f"{API_URL}?{urlencode(params)}"))
        videos.extend(page_videos)
        if not page_token:
            break
    videos.sort(key=lambda video: video["published"], reverse=True)
    return videos


def fetch_records(groups):
    api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    playlist_videos = {}
    channel_videos = []
    for group in groups:
        if group["playlist_id"]:
            if api_key:
                playlist_videos[group["playlist_id"]] = fetch_api_playlist(group["playlist_id"], api_key)
            else:
                playlist_videos[group["playlist_id"]] = parse_feed_videos(
                    fetch_url(PLAYLIST_FEED_URL.format(playlist_id=group["playlist_id"]))
                )
        elif group["title_pattern"] and not channel_videos:
            channel_videos = (
                fetch_api_playlist(UPLOADS_PLAYLIST_ID, api_key) if api_key else parse_feed_videos(fetch_url(FEED_URL))
            )
    records = build_records(groups, playlist_videos, channel_videos)
    complete = len(records) == len(groups) and all(record["source"] == "playlist" for record in records)
    return records, ("live" if complete else "live_limited")


def write_cache(records):
    data = {"channel_url": CHANNEL_URL, "playlists_url": PLAYLISTS_URL, "groups": records}
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n")
    return data


def write_freshness_report(mode, status, source, detail=""):
    FRESHNESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "sources": {"youtube": {"status": status, "url": source, "detail": detail}},
    }
    FRESHNESS_PATH.write_text(json.dumps(payload, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="validate and retain the checked-in snapshot")
    parser.add_argument("--strict", action="store_true", help="require every group to resolve through its playlist")
    args = parser.parse_args()
    if args.offline and args.strict:
        parser.error("--offline and --strict cannot be used together")

    if args.offline:
        data = read_cache()
        missing = [group["name"] for group in load_config() if group["name"] not in {g["name"] for g in data["groups"]}]
        write_freshness_report("offline", "offline", PLAYLISTS_URL, "validated checked-in snapshot")
        print(f"Using {len(data['groups'])} cached YouTube reading-group cards.")
        if missing:
            print(
                "Not yet in the snapshot (run a live refresh and commit data/generated/community_reading_groups.json): "
                + ", ".join(missing),
                file=sys.stderr,
            )
        return

    try:
        groups = load_config()
        records, status = fetch_records(groups)
        validate_records(records)
        write_cache(records)
        detail = (
            "every group resolved through its playlist"
            if status == "live"
            else "some groups were skipped or fell back to the channel feed; see warnings above"
        )
        write_freshness_report("live", status, PLAYLISTS_URL, detail)
        if args.strict and status != "live":
            raise RuntimeError(detail)
        print(f"Refreshed {len(records)} YouTube reading-group cards ({detail}).")
    except Exception as error:
        if args.strict:
            raise RuntimeError(f"Strict YouTube refresh failed: {error}") from error
        try:
            data = read_cache()
        except Exception as cache_error:
            raise RuntimeError(
                f"YouTube refresh failed ({error}) and the checked-in snapshot is invalid ({cache_error})"
            ) from error
        write_freshness_report("live", "fallback_cache", PLAYLISTS_URL, f"used checked-in snapshot after error: {error}")
        print(f"YouTube refresh failed ({error}); using {len(data['groups'])} cached reading-group cards.", file=sys.stderr)


if __name__ == "__main__":
    main()
