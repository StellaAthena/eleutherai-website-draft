import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "refresh_youtube_reading_groups.py"
SPEC = importlib.util.spec_from_file_location("refresh_youtube_reading_groups", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_parse_feed_selects_latest_reading_groups():
    payload = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <feed xmlns=\"http://www.w3.org/2005/Atom\" xmlns:yt=\"http://www.youtube.com/xml/schemas/2015\">
      <entry><yt:videoId>ordinary</yt:videoId><title>Project update</title><published>2026-08-01T00:00:00+00:00</published></entry>
      <entry><yt:videoId>newest</yt:videoId><title>Evaluation Reading Group</title><published>2026-07-01T00:00:00+00:00</published></entry>
      <entry><yt:videoId>second</yt:videoId><title>Agents RG session</title><published>2026-06-01T00:00:00+00:00</published></entry>
      <entry><yt:videoId>third</yt:videoId><title>ML Performance Reading Group</title><published>2026-05-01T00:00:00+00:00</published></entry>
      <entry><yt:videoId>fourth</yt:videoId><title>Older Reading Group</title><published>2026-04-01T00:00:00+00:00</published></entry>
    </feed>"""
    recordings = MODULE.parse_feed(payload)
    assert [recording["video_id"] for recording in recordings] == ["newest", "second", "third"]
    assert recordings[0]["date"] == "July 1, 2026"


def test_checked_in_cache_is_valid():
    data = MODULE.read_cache()
    assert len(data["recordings"]) == 3
    assert all("youtube.com/watch?v=" in recording["url"] for recording in data["recordings"])
