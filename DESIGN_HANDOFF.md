# EleutherAI Website Design Handoff

Updated: 2026-08-04 5:34 PM EDT

## Current state

The approved active-navigation design is on `main` at `96a9bea`. Desktop navigation uses muted inactive links and a white underlined current section. Mobile navigation uses a left-hand marker. Nested pages identify their parent section, and Support Us remains green.

The current homepage research panels are approved. Individual research-area pages, including Training Dynamics, are intentionally excluded from `main` and are not a release blocker.

Use the Hugo source as authoritative. Do not edit the old root HTML files or the material under `mockups/` and `clone/` as though they were the production site.

## Recommended design work

### 1. Establish one headline system

Ordinary pages, tools, programs, projects, and articles should use one shared page-title scale. The homepage institutional statement should be the only deliberate exception. Long titles may wrap, but templates should not introduce narrow text columns that force avoidable line breaks.

Before editing templates, inventory the current page-title rules in `site-page.css`, `static/community-impact.css`, `static/research-library.css`, and `static/soar.css`. Replace independent sizes with shared tokens, then verify short and long titles at desktop and mobile widths.

### 2. Define a reusable color palette

Create a visual mock-up before changing production styles. The palette should contain approximately eight contrast-tested colors: the current blue, green, gold, violet, and SOAR coral, plus likely teal, orange, and pink.

For each hue, define:

- A bright accent for rules, icons, and small emphasis
- A dark filled-surface color for panels
- A faint tint for restrained backgrounds
- Tested text colors for each surface

Colors should be selected compositionally rather than permanently assigned to research areas. Reserve fixed semantic colors only for genuine states or distinctions. Avoid using very dark link text on the homepage's colored panels; the prior audit found that treatment failed normal-text contrast.

### 3. Centralize publication distinctions

The Research Library currently maps oral, spotlight, runner-up, and best-paper distinctions locally in `layouts/_default/research-library.html`. Move this mapping into one shared Hugo partial or data structure and reuse it everywhere papers appear, including the homepage Latest feed.

Approved symbols:

- Oral: `🎙️`
- Spotlight: `🔦`
- Best-paper runner-up: `🥈`
- Best paper: `🏆`

Each marker needs an accessible text label and a fixed-width gutter so titles and metadata remain aligned whether or not a paper has a distinction.

### 4. Standardize interaction and symbol grammar

Use one external-link arrow treatment across the site. Keep plus/minus symbols for disclosures only. Use familiar icons for profile destinations and other recognizable actions, with accessible labels and hover/focus states.

Review hover, focus, and active states together. Navigation is now standardized, but cards, publication links, sponsor links, and article links still use several unrelated treatments.

### 5. Run a final visual consistency pass

After the design tokens are established, review every published page at desktop and mobile widths. Check typography, color contrast, heading wrapping, vertical rhythm, icon alignment, focus visibility, overflow, and whether repeated components behave consistently.

Do not redesign the main Research page during this pass. Stella plans to rewrite it separately.

## Release and integration work

These branches still contain work not present on `main`:

- `codex/blog-subdomain` at `f06500a`: splits the blog into its own subdomain build. Rebase it onto the new navigation commit before integration and rerun combined main/blog route checks.
- `codex/headcount-netlify` at `362da61`: contains `972be1c` for the authoritative 13-person staff count and `362da61` for Netlify configuration. Review and integrate these commits separately so the content correction and deployment setup remain easy to audit.

The Support Us page still needs a real contribution or contact destination. Stella is deciding what that should be, so do not invent one.

Local `main` is ahead of `origin/main`; confirm the final commit set before pushing.

## Branch boundaries

- Keep all individual research-area work on `codex/research-area-pages`. Do not merge that branch wholesale into `main`.
- Research Library and the general Research page belong on `main`.
- Staff portraits, personal-site links, Scholar links, GitHub links, metadata, favicons, social previews, and the custom 404 are already integrated into `main`.
- `AGENTS.md` is local project guidance and should not be staged unless Stella explicitly asks.

## Build and preview

For a production-data build:

```bash
cd /Users/stellabiderman/Documents/research/Codex/eleutherai_homepage_draft
make build
```

For a reproducible offline check and local preview:

```bash
cd /Users/stellabiderman/Documents/research/Codex/eleutherai_homepage_draft
make build-offline
make serve-offline PORT=8068
```

Then open:

```bash
open http://127.0.0.1:8068/
```
