import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "refresh_youtube_reading_groups.py"
SPEC = importlib.util.spec_from_file_location("refresh_youtube_reading_groups", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

PLAYLIST_FEED = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<feed xmlns=\"http://www.w3.org/2005/Atom\" xmlns:yt=\"http://www.youtube.com/xml/schemas/2015\" xmlns:media=\"http://search.yahoo.com/mrss/\">
  <title>Evaluation Reading Group</title>
  <entry><yt:videoId>older</yt:videoId><title>Evaluation Reading Group Session 3: Old Benchmarks</title><published>2026-05-01T00:00:00+00:00</published></entry>
  <entry><yt:videoId>newest</yt:videoId><title>Evaluation Reading Group Session 4: Better Benchmarks</title><published>2026-07-01T00:00:00+00:00</published><media:group><media:description>Evaluation Reading Group meeting recording.

A discussion of how benchmarks fail. A second sentence.</media:description></media:group></entry>
</feed>"""

CHANNEL_FEED = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<feed xmlns=\"http://www.w3.org/2005/Atom\" xmlns:yt=\"http://www.youtube.com/xml/schemas/2015\">
  <entry><yt:videoId>ordinary</yt:videoId><title>Project update</title><published>2026-08-01T00:00:00+00:00</published></entry>
  <entry><yt:videoId>agents</yt:videoId><title>Planning and Agents RG, 2026-06-01 Session: Better Search</title><published>2026-06-01T00:00:00+00:00</published></entry>
</feed>"""


def test_parse_feed_videos_sorts_newest_first():
    videos = MODULE.parse_feed_videos(PLAYLIST_FEED)
    assert [video["video_id"] for video in videos] == ["newest", "older"]


def test_playlist_group_links_into_the_playlist():
    groups = [{"name": "Evaluation Reading Group", "playlist_id": "PLtest", "title_pattern": ""}]
    records = MODULE.build_records(groups, {"PLtest": MODULE.parse_feed_videos(PLAYLIST_FEED)}, [])
    record = records[0]
    assert record["name"] == "Evaluation Reading Group"
    assert record["url"] == "https://www.youtube.com/watch?v=newest&list=PLtest"
    assert record["playlist_url"] == "https://www.youtube.com/playlist?list=PLtest"
    assert record["latest_session_title"] == "Better Benchmarks"
    assert record["date"] == "July 1, 2026"
    assert record["overview"] == "A discussion of how benchmarks fail."
    assert record["source"] == "playlist"


def test_group_without_playlist_falls_back_to_channel_feed_pattern():
    groups = [{"name": "Planning and Agents Reading Group", "playlist_id": "", "title_pattern": r"Planning and Agents RG"}]
    records = MODULE.build_records(groups, {}, MODULE.parse_feed_videos(CHANNEL_FEED))
    record = records[0]
    assert record["url"] == "https://www.youtube.com/watch?v=agents"
    assert record["playlist_url"] == ""
    assert record["latest_session_title"] == "Better Search"
    assert record["source"] == "channel_feed"


def test_cards_sort_by_newest_recording():
    groups = [
        {"name": "Planning and Agents Reading Group", "playlist_id": "", "title_pattern": r"Planning and Agents RG"},
        {"name": "Evaluation Reading Group", "playlist_id": "PLtest", "title_pattern": ""},
    ]
    records = MODULE.build_records(groups, {"PLtest": MODULE.parse_feed_videos(PLAYLIST_FEED)}, MODULE.parse_feed_videos(CHANNEL_FEED))
    assert [record["name"] for record in records] == ["Evaluation Reading Group", "Planning and Agents Reading Group"]


def test_group_with_no_recordings_is_skipped_with_warning(capsys):
    groups = [
        {"name": "Empty Reading Group", "playlist_id": "PLempty", "title_pattern": ""},
        {"name": "Evaluation Reading Group", "playlist_id": "PLtest", "title_pattern": ""},
    ]
    records = MODULE.build_records(groups, {"PLempty": [], "PLtest": MODULE.parse_feed_videos(PLAYLIST_FEED)}, [])
    assert [record["name"] for record in records] == ["Evaluation Reading Group"]
    assert "Empty Reading Group" in capsys.readouterr().err


def test_all_groups_empty_is_an_error():
    groups = [{"name": "Empty Reading Group", "playlist_id": "PLempty", "title_pattern": ""}]
    with pytest.raises(ValueError, match="no reading group produced"):
        MODULE.build_records(groups, {"PLempty": []}, [])


def test_parse_api_videos_extracts_metadata():
    payload = json.dumps(
        {
            "items": [
                {
                    "snippet": {
                        "title": "Evaluation Reading Group Session 9: Reliable Rankings",
                        "description": "A discussion of robust benchmark comparisons. More detail.",
                        "publishedAt": "2026-08-12T12:00:00Z",
                        "resourceId": {"videoId": "api-video"},
                    },
                    "contentDetails": {"videoPublishedAt": "2026-08-10T12:00:00Z"},
                }
            ],
            "nextPageToken": "next-page",
        }
    ).encode()
    videos, next_page = MODULE.parse_api_videos(payload)
    assert next_page == "next-page"
    assert videos[0]["video_id"] == "api-video"
    assert videos[0]["published"] == "2026-08-10T12:00:00Z"


def test_checked_in_config_and_cache_are_valid():
    groups = MODULE.load_config()
    data = MODULE.read_cache()
    assert {record["name"] for record in data["groups"]} <= {group["name"] for group in groups}
    assert all("youtube.com/watch?v=" in record["url"] for record in data["groups"])


def test_live_failure_uses_valid_cache(tmp_path, monkeypatch):
    output = tmp_path / "community_reading_groups.json"
    freshness = tmp_path / "youtube.json"
    output.write_text(MODULE.OUTPUT_PATH.read_text())
    monkeypatch.setattr(MODULE, "OUTPUT_PATH", output)
    monkeypatch.setattr(MODULE, "FRESHNESS_PATH", freshness)
    monkeypatch.setattr(MODULE, "fetch_records", lambda groups: (_ for _ in ()).throw(OSError("offline")))
    monkeypatch.setattr(MODULE.sys, "argv", ["refresh"])
    MODULE.main()
    report = json.loads(freshness.read_text())
    assert report["sources"]["youtube"]["status"] == "fallback_cache"
    assert json.loads(output.read_text())["groups"]
