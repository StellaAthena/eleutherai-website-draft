# EleutherAI Website Design Handoff

Updated: 2026-08-04

## Current state

`main` is at `4a4f52a`. All five recommended design tasks below are complete and committed. The two pending feature branches (`codex/blog-subdomain`, `codex/headcount-netlify`) are also integrated into `main`.

Desktop navigation uses muted inactive links and a white underlined current section. Mobile navigation uses a left-hand marker. Nested pages identify their parent section, and Support Us remains green.

The current homepage research panels are approved. Individual research-area pages, including Training Dynamics, are intentionally excluded from `main` and are not a release blocker.

Use the Hugo source as authoritative. Do not edit the old root HTML files or the material under `mockups/` and `clone/` as though they were the production site.

## Design system — completed

### 1. Headline system ✓

`--title-size: 4rem`, `--title-lh: 1.04`, and `--title-mobile: 2.45rem` are defined in the `:root` block of `site-page.css` and used by all non-homepage hero h1s. Community Impact, SOAR, and Research Library were updated; each also has an explicit mobile override at 680px (the page-specific class selectors would otherwise win over the generic `h1` rule in the media query). The homepage hero (`clamp(3.2rem, 6.2vw, 5.1rem)`) remains the only deliberate exception.

### 2. Color palette ✓

Eight accent tokens are in `:root`: `--green`, `--blue`, `--gold`, `--violet`, `--coral` (bright accents) and `--blue-surface`, `--gold-surface`, `--green-surface`, `--violet-surface` (dark filled-surface colors for the priority cards). The WCAG AA failure on priority-card link hover — `color: #081018` on all four panel backgrounds — is fixed: hover now increases `text-decoration-thickness` from 1px to 2px instead of changing color. The SOAR coral (`--soar-safety`) and the Research Library's `--lib-green` have been aliased to the palette tokens.

### 3. Publication distinctions ✓

`layouts/partials/paper-marker.html` is the single source for the 🎙️ 🔦 🥈 🏆 markers with accessible `role="img"` and `aria-label`. Both `layouts/_default/research-library.html` and `layouts/partials/publication-groups.html` use the partial.

### 4. Interaction and symbol grammar ✓

All `->` link arrows are standardized to `→`. `.link` and `.back-link` now have `text-decoration: underline` on `:hover`/`:focus-visible`. `.button` and `.button.primary` have hover and focus-visible states (border highlight and brightness, respectively). Every interactive element — nav links, cards, publication items, staff icons, donor logos, footer links — has a corresponding `:focus-visible` rule.

### 5. Final visual consistency pass ✓

No oversized h1s remain outside the homepage hero. No `->` arrows remain in templates. No obvious mobile overflow issues. The remaining hardcoded hex values in `site-page.css` are intentional: `#fff` for white text on colored panels, `#f2d77b` for a lighter gold used as badge text (the token `--gold` is too dark for that use), and near-black surface variants (`#0c1118`, `#10161d`, `#111820`) for specific element backgrounds. Do not redesign the main Research page — Stella plans to rewrite it separately.

## Open items

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
