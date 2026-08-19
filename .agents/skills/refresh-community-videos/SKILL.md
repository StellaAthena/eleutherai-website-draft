---
name: refresh-community-videos
description: Refresh and verify the three recent EleutherAI YouTube reading-group recordings shown on the Community page. Use when building the website with current online data, when the Community video list looks stale or incorrect, or when maintaining the YouTube selection rules and fallback snapshot.
---

# Refresh Community Videos

Keep the Community page current using official YouTube metadata without introducing hand-written titles or summaries.

## Workflow

1. Run `python3 scripts/refresh_youtube_reading_groups.py` from the repository root. A normal `make build` runs this automatically.
2. Inspect `data/generated/community_reading_groups.json`. Confirm it contains exactly three recordings in newest-first order and that each is genuinely a reading-group session.
3. Run `python3 -m pytest -q tests/test_youtube_reading_groups.py`.
4. Run `make freshness` and report whether discovery used the complete uploads playlist, the limited Atom feed, or the checked-in cache.
5. Build the site and inspect `/community/` at desktop and mobile widths.
6. Report the three selected titles and links to the user. Do not silently change selection rules.

## Selection Rules

- Source only from the official EleutherAI channel. Prefer the paginated uploads playlist through `YOUTUBE_API_KEY`; use the channel Atom feed only as the explicitly reported limited fallback.
- Match titles containing `Reading Group` or `RG` as a standalone abbreviation, case-insensitively.
- Select the three newest matches by YouTube publication timestamp.
- Extract the session title and reading-group name from the official upload title.
- Use the first substantive sentence of the official description for the overview. Keep any necessary fallback concise and source-grounded.
- Treat `data/generated/community_reading_groups.json` as a checked-in fallback, not the editorial source of truth.

If a valid reading-group upload is omitted because its title does not match these rules, explain the exception and ask before broadening the matcher. If the feed format changes, update the parser and tests together.
