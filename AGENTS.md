# EleutherAI Website Agent Instructions

These instructions apply to AI agents working in this repository. Treat them as project requirements, not optional style suggestions.

## Project purpose

Build a serious, legible, research-first website for EleutherAI. The site should demonstrate EleutherAI's work through concrete papers, models, datasets, tools, people, metrics, and outcomes. It should not read like a generic AI-company landing page or a stylized fake terminal.

The repository produces two related Hugo sites:

- Main site: `https://www.eleuther.ai/`
- Blog: `https://blog.eleuther.ai/`

The sites share layouts, styling, data, and assets but are built and deployed separately.

## Before changing anything

1. Read the relevant content, data, template, and CSS files before proposing a change.
2. Check `git status`, the current branch, and active worktrees. Do not assume the checkout is clean or that another agent is not working nearby.
3. Keep exploratory design work on an isolated feature branch or worktree until Stella approves it.
4. Coordinate preview ports and shared-file ownership with concurrent agents.
5. Never merge, push, or modify `main` unless Stella explicitly authorizes it.
6. Preserve unrelated user and agent changes. Do not clean up or revert work outside the assigned scope.

Do not stage or commit this `AGENTS.md` file unless Stella explicitly asks.

## Design workflow

For layout, information architecture, homepage, navigation, research, community, staff, or visual-polish work, use a design-first process even when Stella does not explicitly request one.

1. Decide what belongs on the page, what belongs on a subpage, and what should be omitted.
2. Sketch the page structure using realistic public content. Do not put editorial notes or implementation labels in the rendered mockup.
3. Critique the proposed structure before implementation. Identify what could feel bloated, gimmicky, generic, thin, or difficult to maintain.
4. Present two or three genuinely distinct directions when the visual choice is unclear.
5. Implement only after the direction is clear unless Stella explicitly requests immediate editing.
6. Build and inspect the result at desktop and mobile sizes.
7. Critique the rendered result for hierarchy, spacing, density, readability, wrapping, overflow, and visual continuity.
8. Iterate before reporting completion. A successful Hugo build is not visual QA.

After every substantive visual change, provide the exact preview URL. When reporting a website change, also provide the build and open commands.

## Source organization

Keep editable content separate from templates and styling.

- `content/`: main-site Markdown and news posts
- `content-blog/`: blog posts and blog front matter
- `data/`: editable structured content and generated Hugo data
- `layouts/`: Hugo templates and shared partials
- `site-page.css`: shared site-wide visual system
- `static/`: page-specific CSS, JavaScript, icons, and public assets
- `assets/`: source images and shared brand assets mounted by Hugo
- `generate_hugo_data.py`: publication, research, homepage-metric, and blog-index generation

Prefer Markdown or YAML for copy changes. Change a template only when page structure or behavior must change. Do not embed maintainable content directly in HTML when it belongs in `content/` or `data/`.

## Data sources and generated files

### Publications

The EleutherAI papers Google Sheet is the source of truth:

`https://docs.google.com/spreadsheets/d/1LcB7_1lHZgO8_EmOkrvfV2BTaOngX95J5v8PJeuN4rM/edit?usp=sharing`

A normal live build downloads the Sheet, regenerates the publication library and homepage publication data, and then builds Hugo.

A paper requires a title, `Sort Date`, and complete semicolon-separated `all authors` value. `Display Authors` supplies the public author line, `all authors` supplies the author-search index, semicolon-separated `Area` values supply research metadata, and `Superlative` supplies distinctions. A link makes the rendered entry clickable.

Do not manually edit these generated files:

- `eleutherai_papers.csv`
- `data/research/papers.json`
- `data/research/library_papers.json`
- `data/research/paper_groups.json`
- `data/research/homepage_papers.json`
- `data/research/homepage_paper_groups.json`
- `data/research/area_papers.json`
- `data/home_generated_metrics.json`
- `data/blog_posts.json`

Edit the Sheet or the appropriate editable YAML and regenerate the outputs.

The current `datasets` research grouping is a filtered set of publication records, not an inventory of released dataset artifacts. The build does not currently import a Hugging Face dataset catalog or dataset-download metric. Do not describe it as doing so.

### Homepage and news

Homepage metrics, research priorities, links, and manual news live in `data/home.yaml`.

The homepage `Latest` feed combines:

- posts from `content-blog/`
- news from `content/news/`
- dated manual items from `data/home.yaml`

It sorts the combined feed chronologically and displays the four newest items. Do not create a second hand-ordered copy in a template.

### Staff and assets

Staff data lives in `data/staff.yaml`. Store portraits under `static/assets/staff/`. Do not hotlink staff portraits or core site assets from the old website or third-party CDNs.

## Build and preview

Use the Makefile rather than inventing parallel build commands.

### Main site with live data

```bash
make build
make serve-offline PORT=8060
open http://127.0.0.1:8060/
```

For live-reloading development with a fresh data pull:

```bash
make serve PORT=8060
```

### Main site and blog

```bash
make build-all
```

Preview in separate terminals:

```bash
make serve-offline PORT=8060
make serve-blog-offline PORT=8061
```

Then open:

```bash
open http://127.0.0.1:8060/
open http://127.0.0.1:8061/
```

### Offline verification

```bash
make build-offline
make build-all-offline
```

Offline targets use checked-in snapshots and do not check the Google Sheet for new publications. Do not use an offline build to claim live data is current.

If a preview port is occupied on macOS, stop the existing process before starting another server:

```bash
PID=$(lsof -ti tcp:8060); if [ -n "$PID" ]; then kill "$PID"; fi
```

The production main-site Netlify configuration runs `make build` and publishes `public/`. The blog configuration under `netlify/blog/` runs `make build-blog` and publishes `public-blog/`.

## Visual system

### Overall character

- Keep the site dark, minimal, precise, and institutional.
- Prefer authentic research artifacts and project imagery over decoration.
- Do not use fake-terminal styling, generic technology illustrations, decorative gradients, glowing blobs, or invented scientific diagrams when genuine work is available.
- Do not make the site look like a SaaS dashboard or a stack of promotional cards.

### Color

The shared palette is defined in `site-page.css`: green, blue, gold, violet, and coral, with related surface colors.

- Use the palette consistently across the site.
- When a list or sequence gives each item its own highlight color, assign colors in this order: blue, green, violet, gold, coral. For sequences longer than five items, cycle back to blue and repeat the same order.
- Use color for hierarchy, publication distinctions, links, and selected featured material.
- Do not permanently assign one color to each research area. Research areas overlap and the taxonomy will grow.
- Do not make every section a differently colored panel.
- Preserve sufficient contrast in all states.

### Typography and width

- Use the shared page-title scale and established heading levels. Do not invent a new headline system for each page.
- Do not end headings with periods.
- Put explanatory copy below its heading by default. Do not place paragraphs beside section headings unless the composition has a specific content-driven reason.
- The global `.wrap` defines the intended page frame. Do not make text extend to the viewport edges.
- Within that frame, do not add arbitrary `max-width` constraints that make headings or body text wrap earlier than the available layout requires.
- Do not use viewport-scaled font sizes.
- Make text fit at mobile and desktop sizes without overlapping adjacent content.

### Labels, rules, and containers

- Do not add decorative eyebrow labels or small labels that repeat a nearby heading.
- Use horizontal rules sparingly. Prefer spacing, alignment, typography, and background changes for grouping. Retain a rule only when it communicates real structure.
- Use cards for repeated objects such as people, projects, or a deliberately comparable set of items.
- Do not put cards inside cards.
- Do not turn every section into a bordered box or floating panel.
- Avoid highly uniform grids when the content has different importance or evidence. Use imagery, varied scale, and editorial composition when appropriate.
- Keep fixed-format controls dimensionally stable so interaction and dynamic content do not shift the layout.

### Content and evidence

- Prefer proof over explanation: show papers, models, datasets, code, people, metrics, and outcomes.
- Do not add generic filler, temporary marketing copy, or explanations of the site's taxonomy and maintenance logic.
- Do not add visible process narration, mockup ribbons, audience labels, page-logic notes, or instructions for using the page.
- A mockup must contain only material suitable for publication. When copy is genuinely undecided, use `Lorem ipsum` rather than inventing claims.
- Never invent people, organizations, sponsorships, numbers, awards, publications, or links.

### Images

- Use images that show the real project, research result, tool, dataset, model, person, or community.
- Do not use dark atmospheric stock imagery when the visitor needs to inspect the subject.
- Preserve source aspect ratios unless a deliberate crop has been approved.
- Verify that every image loads and remains correctly framed at desktop and mobile widths.

### Publication distinctions

Render publication distinctions through `layouts/partials/paper-marker.html` everywhere they appear:

- `oral`: microphone symbol, blue
- `spotlight`: flashlight symbol, green
- `runnerup`: silver-medal symbol, award color
- `bestpaper`: trophy symbol, award color

Do not create page-specific symbols for the same distinction. Every symbol needs an accessible label. A qualifying recent paper should retain its distinction on the homepage as well as in the Research Library.

## Information architecture

The initial public research architecture is intentionally limited to:

- one Research landing page
- the searchable Research Library
- selected mature project pages such as Pythia

Individual research-area pages are deferred. Do not expose unfinished area routes through navigation, homepage cards, sitemaps, or calls to action. Homepage research themes should link to mature public artifacts or the main Research page.

Research Areas are the normal public vocabulary. Broad categories such as Capabilities, Interpretability, and Safety are separate, overlapping metadata rather than parents in a strict hierarchy. Do not infer a category from an area or force areas into exclusive program ownership.

Keep research communication pages distinct from research artifacts:

- Communication pages explain a project, agenda, or research direction.
- The Research Library provides searchable access to papers.
- Project links should lead to real papers, repositories, models, datasets, and documentation.

## Navigation and accessibility

- Preserve the responsive desktop and mobile navigation.
- Preserve `aria-current` so the current page or parent section is programmatically identifiable.
- Use semantic headings, links, buttons, lists, and navigation elements.
- Keep keyboard focus states visible.
- Use familiar icons for controls and provide tooltips or labels when meaning is not obvious.
- External links opened in a new tab must use `rel="noopener noreferrer"`.
- Do not hide essential navigation at mobile breakpoints.

## Required verification

Before reporting a code or design change as complete:

1. Build the affected site or both sites when shared code changed.
2. Run `git diff --check`.
3. Inspect affected pages in a real browser at desktop and mobile widths.
4. Check horizontal overflow, wrapping, images, navigation, keyboard focus, and console errors.
5. Confirm internal links and local assets resolve.
6. Confirm generated data changed through its source rather than by hand.
7. Compare the result with the surrounding site, not only with the edited component.
8. Keep unapproved experiments isolated from `main`.

Baseline verification:

```bash
make build-all-offline
git diff --check
```

For changes affecting publications, news, blog indexing, citations, or homepage metrics, also run a live build:

```bash
make build-all
```

When changing shared layouts, navigation, CSS, logos, favicons, or social metadata, test both the main site and a representative long technical blog post.

## Reporting

When handing work back to Stella:

- State the branch and commit hash.
- List the files changed and the behavior changed.
- Report the exact build and browser QA performed.
- Give the preview URL.
- Include commands to rebuild and open the site.
- State whether the work is committed, pushed, merged, or still isolated.
- Call out unresolved factual, content, or design decisions without guessing.
