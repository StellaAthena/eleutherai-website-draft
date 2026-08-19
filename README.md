# EleutherAI Website

This repository contains the Hugo source for the EleutherAI website and blog.

- Main site: [www.eleuther.ai](https://www.eleuther.ai/)
- Blog: [blog.eleuther.ai](https://blog.eleuther.ai/)
- Publication source of truth: [EleutherAI papers Google Sheet](https://docs.google.com/spreadsheets/d/1LcB7_1lHZgO8_EmOkrvfV2BTaOngX95J5v8PJeuN4rM/edit?usp=sharing)

The main site and blog share templates, styles, data, and assets, but Hugo builds them as separate sites for separate Netlify deployments.

## Build and view the website

The build requires Python 3.12 or newer, Make, and Hugo Extended 0.158.0. The supported versions are recorded in `.python-version` and `.hugo-version`.

For a new local checkout, install the development dependencies in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
playwright install chromium
make check-tools
```

Playwright is used only for refreshing the Hugging Face download metric. Offline builds and tests do not launch a browser.

From the repository root, build the main site with current online data:

```bash
make build
```

The static output is written to `public/`. Preview the completed build locally:

```bash
make serve-offline PORT=8060
open http://127.0.0.1:8060/
```

For normal editing with Hugo's live-reloading server:

```bash
make serve PORT=8060
```

This refreshes the online data before starting the server.

Build both the main site and blog:

```bash
make build-all
```

Preview the blog separately:

```bash
make serve-blog-offline PORT=8061
open http://127.0.0.1:8061/
```

When internet access is unavailable, use the checked-in data snapshots:

```bash
make build-offline
make build-all-offline
```

Offline builds do not check the publication Sheet, refresh online metrics, or query YouTube. They validate and use the checked-in snapshots instead.

## Where to add content

Most text should be added to Markdown under `content/` or structured YAML under `data/`. The files under `layouts/` determine how that content is arranged. CSS and public assets live under `site-page.css`, `static/`, and `assets/`.

Files directly under `data/` and `data/projects/` are maintained by people. Everything under `data/generated/` is written by the build scripts and must not be edited directly. Change the relevant Google Sheet, Markdown, YAML, external source, or generator and rebuild.

### Page-by-page guide

| Content | Edit here | Notes |
| --- | --- | --- |
| Homepage hero and section structure | [`layouts/index.html`](layouts/index.html) | The homepage's main prose and arrangement currently live in the template. |
| Homepage metrics, Current Research links, manual news | [`data/home.yaml`](data/home.yaml) | Generated metric values replace entries that have a `source` key. Recent outputs are generated from the papers Sheet and blog front matter. |
| About page | [`content/about.md`](content/about.md) | Donor logos and links are stored separately in `data/donors.yaml`. |
| Community page | [`data/community.yaml`](data/community.yaml) | `content/community.md` contains only the page front matter. |
| Community reading-group videos | [EleutherAI YouTube](https://www.youtube.com/@Eleuther_AI) | The build refreshes [`data/generated/community_reading_groups.json`](data/generated/community_reading_groups.json); use the repository's `refresh-community-videos` skill when maintaining or troubleshooting it. |
| Staff page | [`data/staff.yaml`](data/staff.yaml) | Store portraits locally under `static/assets/staff/`. |
| Research introduction | [`content/research/_index.md`](content/research/_index.md) | The publication list below it is generated automatically. |
| Research Library | [Google Sheet](https://docs.google.com/spreadsheets/d/1LcB7_1lHZgO8_EmOkrvfV2BTaOngX95J5v8PJeuN4rM/edit?usp=sharing) | `content/papers.md` only defines the route and layout. Do not hand-edit the rendered paper list. |
| Pythia project page | [`data/projects/pythia.yaml`](data/projects/pythia.yaml) | The page title and summary are in `content/projects/pythia.md`. |
| SOAR page | [`data/soar.yaml`](data/soar.yaml) | The page title and description are in `content/soar.md`. |
| News post | [`content/news/`](content/news/) | Dated news posts can enter the homepage Latest feed. |
| Manual homepage news item | [`data/home.yaml`](data/home.yaml) under `manual_news` | Give the item a title, URL, and date if it should participate in chronological sorting. |
| Blog post | [`content-blog/`](content-blog/) | Add Markdown front matter with at least `title` and `date`. |
| General standalone page | [`content/`](content/) | Most ordinary Markdown pages use a template under `layouts/_default/`. |
| Header and navigation | [`layouts/partials/header.html`](layouts/partials/header.html) | Shared by the main site and blog. |
| Footer | [`layouts/partials/footer.html`](layouts/partials/footer.html) | Shared by the main site and blog. |
| Shared styling | [`site-page.css`](site-page.css) | Page-specific styles are under `static/`, such as `research-library.css`. |
| Logos and source images | [`assets/`](assets/) | Hugo mounts selected assets into the built sites. |
| Directly served assets | [`static/`](static/) | Files retain their paths in the generated site. |

### Directories that are not content sources

- `public/` and `public-blog/` are generated build outputs. Do not edit them.
- `/blog/` and `blog.html` remain under review as possible deployment artifacts. Do not change or remove them until that deployment is confirmed.
- `generate_blog_pages.py` belongs to the older standalone blog export and is not called by the current Makefile.

## What the build process does

The Makefile coordinates data refreshes and Hugo. The normal main-site build is:

```text
make build
  -> python3 generate_hugo_data.py
  -> python3 scripts/refresh_youtube_reading_groups.py
  -> hugo --cleanDestinationDir
```

Each stage has a different purpose.

### YouTube reading-group refresh

`scripts/refresh_youtube_reading_groups.py` selects the three newest videos whose titles contain `Reading Group` or the standalone abbreviation `RG`. With `YOUTUBE_API_KEY` set, it paginates through the channel's complete uploads playlist. Without that key, an ordinary build uses YouTube's limited recent Atom feed and records that limitation in the freshness report. It extracts a concise session title and reading-group name, uses the first substantive sentence of the official description as the topic overview, and writes those fields with the publication date, video ID, and link to `data/generated/community_reading_groups.json`.

The checked-in JSON file is the deterministic offline fallback. A live build warns and uses that snapshot if YouTube is temporarily unavailable; it fails only when neither online discovery nor a valid three-video snapshot is available. `make build-offline` never queries YouTube and validates the snapshot before Hugo runs. `make verify-live` requires `YOUTUBE_API_KEY` so it can prove that the selection came from the complete uploads history.

## Data generation: `generate_hugo_data.py`

The normal build runs this script online. It fetches external data, normalizes publication records, derives display fields, and writes JSON for Hugo.

### 1. Refresh the publication Sheet

The script downloads a cache-busted CSV export of the papers tab and writes it to:

```text
eleutherai_papers.csv
```

The script verifies the full expected header set before replacing the local snapshot. If the Sheet cannot be downloaded, or its schema changes unexpectedly, a live build stops instead of silently claiming that stale publication data is current.

The principal Sheet columns currently used are:

| Sheet column | How the website uses it |
| --- | --- |
| `Title` | Display title and record identity |
| `Sort Date` | Determines whether a paper enters the public library; supplies its displayed year and chronological sort |
| `Highest Impact` | Selects papers for the generated homepage Recent outputs candidate set; checked rows export as `TRUE` |
| `Display Authors` | Author line shown in the Research Library |
| `All Authors` | Complete semicolon-separated author list used for author search and metadata generation |
| `Area` | Semicolon-separated research-area metadata used by generated collections and filters |
| `Link` | Makes the paper entry clickable |
| `Conference or Journal` | Primary archival venue; blank values fall back to a workshop or arXiv |
| `Workshop` | Workshop appearance; may coexist with an archival venue |
| `Superlative` | Oral, spotlight, best-paper, and runner-up text and symbols |

A row must have both a normalized title and a parseable `Sort Date` to appear in the main Research Library and publication count.

### 2. Normalize links, dates, and venues

The script cleans OpenReview tracking parameters and uses a small URL override table for known papers whose links were missing or incorrect in earlier data.

Venue logic is derived from `Conference or Journal` and `Workshop`:

- Papers use the conference or journal, then a workshop if no archival venue exists, then arXiv as a fallback.
- Papers with both an archival venue and a distinct workshop can produce separate appearances in grouped publication data.

The generator maps the simplified Sheet schema into its internal publication model:

- `Sort Date` controls inclusion and the one-record-per-paper library chronology.
- The same date is used for conference and workshop appearance sorting because the Sheet intentionally maintains one date per paper.
- arXiv groups are normalized to January 1 so they are treated as the earliest chronological point in their year and appear after later conference and workshop groups in the newest-first display.
- Workshop sort dates receive a seven-day offset so a corresponding main conference is presented above its workshops.

That final ordering rule is editorial rather than historical: it keeps main conferences visually prominent even when their workshops occurred later.

### 3. Derive publication distinctions

The script cleans the `Superlative` field and associates an award with the appropriate conference or workshop appearance. Commas inside a single award description are preserved. For the Research Library it chooses one marker using this precedence:

1. runner-up or finalist
2. best paper
3. spotlight
4. oral

The generated `marker` value is rendered by `layouts/partials/paper-marker.html`, which keeps symbols and accessible labels consistent across the site.

### 4. Build publication representations

The website needs two related but different publication representations.

#### Publication appearances

`all_papers()` can create more than one record for a paper when it appeared at both a workshop and an archival venue. Each appearance contains:

- title and URL
- publication year
- venue and venue year
- venue kind: conference, workshop, or arXiv
- normalized conference family
- group sort date
- appearance-specific distinctions

These records feed the chronological venue-grouped publication components.

#### Research Library records

`library_papers()` creates exactly one record per dated paper. In addition to title, URL, year, and venue, each record contains:

- authors, displayed as last names and shortened after four names
- status
- primary and additional areas
- lead organization
- EleutherAI contact
- artifact type, currently `Paper`
- distinction marker and text

The current public Research Library does not display every stored metadata field, but the fields remain available to its filters and templates.

### 5. Generate venue groups

`grouped_papers()` groups publication appearances first by conference family and year, then by track or workshop. Examples include a main ICML conference group, a named workshop under ICML, and an arXiv preprint group.

Within a year, the generated order favors:

1. main conferences
2. workshops
3. arXiv

Papers inside each venue are sorted in reverse chronological order.

### 6. Generate research-area paper sets

The script creates `data/generated/research/area_papers.json` in two ways:

- Training Dynamics uses the hand-curated titles, summaries, and optional venue labels in `research_area_papers.csv`.
- Other areas use the broad-area, include-term, and exclude-term rules in `research_area_filters.csv`.

The keyword filters search the paper title, superlative, conference or journal, workshop, and semicolon-separated `Area` values. These generated sets are useful data, but individual research-area pages are intentionally not exposed in the current public release.

The `datasets` key in this file is a filtered set of papers about datasets. It is not a catalog of released dataset artifacts, and the build does not currently query Hugging Face for a dataset inventory.

### 7. Refresh homepage metrics

The generator writes `data/generated/home_generated_metrics.json` from three sources.

#### Publications

It counts unique titled Sheet rows with a valid `Sort Date`, rounds the result down to the nearest 25, and appends `+`. The resulting object uses the key `publication_count`.

#### Citations

It fetches EleutherAI's Google Scholar profile, extracts the total citation count, rounds down to the nearest thousand, and appends `+` when the homepage renders it. The successful response is cached in `data/generated/home_scholar_metrics.json`.

If Scholar cannot be refreshed, the script uses the cached value. If no cache exists, it omits the metric rather than failing the full build.

#### Model downloads

It obtains the Hugging Face model-download value in this order:

1. `HF_MODEL_DOWNLOADS` environment variable, when set
2. the rendered EleutherAI publisher analytics page through Playwright
3. the checked-in cache in `data/generated/hf_model_downloads_cache.json`

If neither a live value nor a cache is available, the metric is omitted. This is a model-download metric only; it does not count dataset downloads.

The homepage reads `data/home.yaml`. Metric entries with a `source` such as `publication_count`, `scholar_citations`, or `model_downloads` are filled from `data/generated/home_generated_metrics.json` during Hugo rendering.

### 8. Build the blog index used by the homepage

The generator scans `content-blog/` recursively. It skips the section index and posts marked `draft: true`, then reads each post's title and date. It writes a sorted list to `data/generated/blog_posts.json` with production blog-subdomain URLs.

The homepage combines these blog entries with `content/news/` and dated `manual_news` entries from `data/home.yaml`. `layouts/index.html` sorts the combined feed and displays the four newest items.

### 9. Write generated research files

The first pass writes:

| Generated file | Contents |
| --- | --- |
| `data/generated/research/papers.json` | All publication appearances, including separate workshop and conference appearances |
| `data/generated/research/homepage_papers.json` | The first 10 publication appearances |
| `data/generated/research/paper_groups.json` | All appearances grouped by venue family, year, and track |
| `data/generated/research/homepage_paper_groups.json` | Grouped data from the first 30 appearances |
| `data/generated/research/area_papers.json` | Curated and keyword-filtered research-area paper sets |
| `data/generated/research/library_papers.json` | One searchable record per dated paper |
| `data/generated/research/paper_collections.json` | Named publication collections such as SOAR |
| `data/generated/home_generated_metrics.json` | Publication, citation, and model-download homepage values |
| `data/generated/home_scholar_metrics.json` | Last successful Scholar response used as a fallback |
| `data/generated/hf_model_downloads_cache.json` | Last supplied or successfully fetched download value |
| `data/generated/blog_posts.json` | Dated blog entries used by the homepage Latest feed |
| `data/generated/home_recent_outputs.json` | Four newest items from highest-impact papers and published blog posts |
| `data/generated/community_reading_groups.json` | Three newest selected reading-group recordings |

Do not edit these files directly. Edit their source data and rebuild.

## Author search

The Sheet's semicolon-separated `all authors` column is the sole source for complete publication authorship. `generate_hugo_data.py` puts every full name into the hidden Research Library search index while continuing to display the shorter `Display Authors` line. A live or offline build stops with a list of affected titles if any paper has a blank `all authors` cell; fix the Sheet rather than adding a local author override.

## Hugo rendering

After data generation, `hugo --cleanDestinationDir` renders the main site with `hugo.toml` and writes `public/`.

Important data connections include:

- `layouts/index.html` reads `data/home.yaml` and generated homepage data under `data/generated/`.
- `layouts/_default/research-library.html` reads `data/generated/research/library_papers.json`.
- `layouts/_default/research.html` and `layouts/partials/publication-groups.html` read the grouped publication data.
- `layouts/_default/community.html` reads `data/community.yaml`.
- `layouts/_default/staff.html` reads `data/staff.yaml`.
- `layouts/_default/soar.html` reads `data/soar.yaml` and the SOAR paper collection.
- `layouts/_default/pythia.html` reads `data/projects/pythia.yaml`.

`make build-all` performs the complete main-site process above and then builds the blog with `hugo-blog.toml` into `public-blog/`. A standalone `make build-blog` does not refresh publication data first; it uses the generated data already present in the checkout.

## Before committing a content change

For ordinary content that does not depend on external data:

```bash
make verify
```

For publications, homepage metrics, news aggregation, or other externally sourced data:

```bash
make verify-live
```

`make verify` runs the tests, regenerates checked-in snapshots offline, builds both deployments with Hugo warnings treated as errors, checks local links and assets, and fails if generated snapshots differ from `HEAD` or the diff contains whitespace errors. GitHub Actions runs the same command.

`make verify-live` additionally requires every external source to be current. Set `YOUTUBE_API_KEY` for complete YouTube uploads discovery and either install Playwright or provide `HF_MODEL_DOWNLOADS`. Run `make freshness` after any build to see which sources were fetched live and which used snapshots.

Review the affected main-site and blog pages locally before committing generated changes.
