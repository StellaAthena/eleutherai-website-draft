import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "refresh_youtube_reading_groups.py"
SPEC = importlib.util.spec_from_file_location("refresh_youtube_reading_groups", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_parse_feed_selects_latest_reading_groups():
    payload = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <feed xmlns=\"http://www.w3.org/2005/Atom\" xmlns:yt=\"http://www.youtube.com/xml/schemas/2015\">
      <entry><yt:videoId>ordinary</yt:videoId><title>Project update</title><published>2026-08-01T00:00:00+00:00</published></entry>
      <entry><yt:videoId>newest</yt:videoId><title>Evaluation Reading Group Session 4: Better Benchmarks</title><published>2026-07-01T00:00:00+00:00</published><media:group xmlns:media=\"http://search.yahoo.com/mrss/\"><media:description>Evaluation Reading Group meeting recording.\n\nA discussion of how benchmarks fail. A second sentence.</media:description></media:group></entry>
      <entry><yt:videoId>second</yt:videoId><title>Planning and Agents RG, 2026-06-01 Session: Better Search</title><published>2026-06-01T00:00:00+00:00</published></entry>
      <entry><yt:videoId>third</yt:videoId><title>ML Performance Reading Group Session 3: Faster Serving</title><published>2026-05-01T00:00:00+00:00</published></entry>
      <entry><yt:videoId>fourth</yt:videoId><title>Older Reading Group</title><published>2026-04-01T00:00:00+00:00</published></entry>
    </feed>"""
    recordings = MODULE.parse_feed(payload)
    assert [recording["video_id"] for recording in recordings] == ["newest", "second", "third"]
    assert recordings[0]["date"] == "July 1, 2026"
    assert recordings[0]["session_title"] == "Better Benchmarks"
    assert recordings[0]["reading_group"] == "Evaluation Reading Group"
    assert recordings[0]["overview"] == "A discussion of how benchmarks fail."
    assert recordings[1]["session_title"] == "Better Search"
    assert recordings[1]["reading_group"] == "Planning and Agents Reading Group"


def test_checked_in_cache_is_valid():
    data = MODULE.read_cache()
    assert len(data["recordings"]) == 3
    assert all("youtube.com/watch?v=" in recording["url"] for recording in data["recordings"])


def test_parse_api_page_extracts_reading_group_metadata():
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
                },
                {
                    "snippet": {
                        "title": "Unrelated project update",
                        "publishedAt": "2026-08-11T12:00:00Z",
                        "resourceId": {"videoId": "ignored"},
                    }
                },
            ],
            "nextPageToken": "next-page",
        }
    ).encode()
    recordings, next_page = MODULE.parse_api_page(payload)
    assert next_page == "next-page"
    assert [recording["video_id"] for recording in recordings] == ["api-video"]
    assert recordings[0]["session_title"] == "Reliable Rankings"
    assert recordings[0]["published"] == "2026-08-10T12:00:00Z"
    assert recordings[0]["overview"] == "A discussion of robust benchmark comparisons."


def test_live_failure_uses_valid_cache(tmp_path, monkeypatch):
    output = tmp_path / "community_reading_groups.json"
    freshness = tmp_path / "youtube.json"
    output.write_text(MODULE.OUTPUT_PATH.read_text())
    monkeypatch.setattr(MODULE, "OUTPUT_PATH", output)
    monkeypatch.setattr(MODULE, "FRESHNESS_PATH", freshness)
    monkeypatch.setattr(MODULE, "fetch_recordings", lambda: (_ for _ in ()).throw(OSError("offline")))
    monkeypatch.setattr(MODULE.sys, "argv", [str(MODULE.SCRIPT_PATH) if hasattr(MODULE, "SCRIPT_PATH") else "refresh"])
    MODULE.main()
    report = json.loads(freshness.read_text())
    assert report["sources"]["youtube"]["status"] == "cache"


def test_strict_mode_rejects_limited_atom_discovery(tmp_path, monkeypatch):
    monkeypatch.setattr(MODULE, "OUTPUT_PATH", tmp_path / "community_reading_groups.json")
    monkeypatch.setattr(MODULE, "FRESHNESS_PATH", tmp_path / "youtube.json")
    cached = json.loads((Path(__file__).resolve().parents[1] / "data" / "generated" / "community_reading_groups.json").read_text())
    monkeypatch.setattr(MODULE, "fetch_recordings", lambda: (cached["recordings"], "live_limited", MODULE.FEED_URL))
    monkeypatch.setattr(MODULE.sys, "argv", ["refresh", "--strict"])
    with pytest.raises(RuntimeError, match="YOUTUBE_API_KEY"):
        MODULE.main()
