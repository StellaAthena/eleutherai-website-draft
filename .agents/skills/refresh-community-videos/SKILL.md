---
name: refresh-community-videos
description: Refresh and verify the reading-group cards shown on the Community page, one per reading-group series (YouTube playlist). Use when building the website with current online data, when the Community cards look stale or incorrect, or when adding a reading group or maintaining the fallback snapshot.
---

# Refresh Community Videos

Keep the Community page's reading-group cards current using official YouTube metadata without introducing hand-written titles or summaries.

## Workflow

1. Check `data/reading_groups.yaml`. Every series should have a `playlist_id` copied from https://www.youtube.com/@Eleuther_AI/playlists (the `list=` value in a playlist URL). Add new reading groups there; the card title is the `name`.
2. Run `python3 scripts/refresh_youtube_reading_groups.py` from the repository root. A normal `make build` runs this automatically.
3. Inspect `data/generated/community_reading_groups.json`. Confirm one entry per configured series, each linking to the newest recording inside its playlist (`watch?v=...&list=...`), sorted newest first.
4. Run `python3 -m pytest -q tests/test_youtube_reading_groups.py`.
5. Run `make freshness`. `live` means every series resolved through its playlist; `live_limited` means at least one fell back to matching the channel feed by `title_pattern` and needs its playlist ID filled in.
6. Build the site and inspect `/community/` at desktop and mobile widths.
7. Report the series names and links to the user. Do not silently change selection rules.

## Selection Rules

- Source only from the official EleutherAI channel. The playlist is the source of truth for which recordings belong to a series.
- For each series, select the single newest recording by YouTube publication timestamp.
- Show the series name as the card title; show the recording's own session title (with the series prefix stripped) and date beneath it.
- Use the first substantive sentence of the official description for the overview. `OVERVIEW_OVERRIDES` in the script exists for descriptions that have no usable sentence; keep overrides concise and source-grounded.
- Treat `data/generated/community_reading_groups.json` as a checked-in fallback, not the editorial source of truth.

If the feed or API format changes, update the parser and tests together.
