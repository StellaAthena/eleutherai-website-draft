# EleutherAI Homepage Visual Audit

## Summary
The homepage has several structural and aesthetic issues that undermine visual hierarchy, readability, and professional presentation. Problems span typography, spacing, alignment, and component design.

---

## Critical Issues

### 1. **Hero Section Imbalance**
**Problem:** The metrics block dominates the hero section, making the descriptive copy feel secondary.
- Headline + copy should be the primary focal point
- Metrics should be supporting evidence, not the main attraction
- Current layout: huge headline → huge metrics → small copy
- **Impact:** Confusing visual hierarchy; visitors don't understand what EleutherAI is before seeing stats

**CSS:** `.home-current-copy h1` (line-height: 1, font-size: 5.1rem max) vs `.home-metric strong` (font-size: 2.25rem max)
**Fix needed:** Reduce headline size slightly, move metrics *after* description, or redesign hero layout

---

### 2. **Typography: Dangerously Tight Line Heights**
**Problem:** Multiple text elements have line-height values that are too tight for large text.

| Element | Line Height | Size | Issue |
|---------|------------|------|-------|
| `.home-current-copy h1` | 1 | 5.1rem | Extremely tight; ascenders/descenders collide |
| `.home-current-copy p` | 1.42 | 1.55rem | Acceptable but tight at larger viewport widths |
| `.home-metric strong` | 1 | 2.25rem | Tight; makes large metrics hard to read |

**Fix:** 
- H1 should be 1.1-1.2 minimum
- Metric values at 2.25rem with line-height: 1 look cramped

---

### 3. **Inconsistent Spacing/Gaps**
**Problem:** Metric spacing is inconsistent and poorly justified.

```css
.home-metric-strip { gap: 22px; }      /* Gap between rows */
.home-metric-row { gap: 18px; }        /* Gap between items in row */
.home-current-copy { margin-bottom: 48px; } /* Above metrics */
```

Why are row gaps (22px) different from item gaps (18px)? No clear system.

**Impact:** Metrics block looks haphazardly arranged, not professionally designed.

---

### 4. **Padding/Border Alignment on Metrics**
**Problem:** Metrics have `padding-top: 16px` + `border-top: 2px`, creating inconsistent top spacing.

```css
.home-metric {
  padding-top: 16px;
  border-top: 2px solid var(--line);
}
```

- The metric label (e.g., "Publications") starts 16px below the border
- Visually, borders look misaligned with the numbers they're under
- Metrics labels (.home-metric span) have `margin-top: 10px`

**Impact:** Metrics feel disconnected from their labels; no clear visual grouping.

---

### 5. **Contrast Problems**

| Color | Value | Usage | WCAG AA? |
|-------|-------|-------|----------|
| --ink | #f4f5f7 (white) | Headlines, metrics values | ✅ Yes (excellent) |
| --body | #c4c9d1 (light gray) | Description text, panel text | ❓ Marginal (~6:1 on #07090d) |
| --muted | #7f8997 (medium gray) | Metadata, labels | ❌ Poor (~4:1 on #07090d) |

**Impact:** `.home-metric span` (labels like "Publications") use `--muted` color at 0.94rem, making them hard to read next to bright metric values.

---

### 6. **Latest Panel Vertical Misalignment**
**Problem:** The "Latest" panel on the right doesn't align with the metrics block properly.

```css
.home-current-layout {
  grid-template-columns: minmax(0, 0.82fr) minmax(320px, 0.42fr);
  gap: 56px;
  align-items: stretch;
}
```

- Metrics: `margin-top: 48px` (applies after h1)
- Latest panel: no offset; starts at same vertical as h1
- Result: Latest panel title appears **higher** than metrics

**Impact:** Uneven baseline; looks unpolished.

---

### 7. **Description Text Cut Off / Visibility**
**Problem:** The descriptive copy ("We build open-source AI infrastructure...") is partially cut off in viewport.

- Text is too long and wraps awkwardly
- Transition phrase "Explore what we are currently excited about:" is cut off the bottom
- No clear "end of section" feeling

**Fix needed:** Either break the description into multiple lines, reduce font size slightly, or restructure the layout.

---

### 8. **Metrics Label Hierarchy Broken**
**Problem:** Metric values and labels don't have clear visual hierarchy.

```css
.home-metric strong {
  font-size: clamp(1.7rem, 3vw, 2.25rem);  /* Values like "150+" */
  line-height: 1;                           /* Too tight */
}
.home-metric span {
  font-size: 0.94rem;                       /* Labels like "Publications" */
  color: var(--muted);                      /* Dark gray, hard to read */
}
```

- Numbers and labels should feel like a unit, but they don't
- Label color (--muted) is too dark
- No visual separation between different metric rows

---

### 9. **Missing Visual System for Sections**
**Problem:** No clear demarcation between hero section and "Current research" section.

- `.home-current-hero` has `border-bottom: 1px solid var(--line)`
- But no section heading or spacing before "Current research" section starts
- Makes page feel like one long list

**Fix:** Add more vertical space, section markers, or a transition element.

---

### 10. **Color Accents Underutilized**
**Problem:** Design defines accent colors (--green, --blue, --gold, --violet) but hero section doesn't use them.

- Hero section is mono-color (white on black)
- No visual interest, no brand personality
- Accent colors only appear in "Current research" cards (is-blue, is-gold, etc.)

**Suggested fix:** Add subtle accent color to metrics or copy to make hero more engaging.

---

## Secondary Issues

### Button/Link Styling
- Support Us button should have better visual emphasis
- Navigation links are subtle; need stronger hover/active states

### Responsive Design Unknowns
- `clamp()` values work, but need to verify they break correctly on mobile
- Hero layout may collapse awkwardly below ~768px
- Latest panel might overflow or break on small screens

### Missing Element: Visual Separation
- No horizontal rule, divider, or section heading between hero and "Current research"
- Page feels like scrolling through unrelated content

---

## Recommendations (Prioritized)

### High Priority
1. **Fix H1 line-height:** Change from `1` to `1.15` minimum
2. **Fix metric label contrast:** Change `.home-metric span` color from `--muted` to `--body`
3. **Realign Latest panel:** Add `margin-top: 48px` to match metrics block
4. **Reduce description text size slightly:** Use `clamp(1rem, 1.5vw, 1.35rem)` instead of current
5. **Increase metric row gaps:** Make spacing consistent (22px everywhere)

### Medium Priority
6. **Add section header/divider** between hero and "Current research"
7. **Improve metric label styling:** Increase size to 0.98rem, use --body color, add letter-spacing
8. **Add accent color to hero:** Subtle color tint or accent underline on headline

### Low Priority
9. **Test responsive breakpoints** at mobile/tablet sizes
10. **Review button styling** on Support Us button

---

## CSS Changes Needed

```css
/* Typography fixes */
.home-current-copy h1 {
  line-height: 1.15;  /* was: 1 */
}

.home-metric strong {
  line-height: 1.15;  /* was: 1 */
}

/* Contrast fixes */
.home-metric span {
  color: var(--body);  /* was: var(--muted) */
  font-size: 0.98rem;  /* was: 0.94rem */
  font-weight: 500;
}

/* Alignment fixes */
.home-latest-panel {
  margin-top: 48px;  /* Match metrics block */
}

/* Spacing consistency */
.home-metric-strip {
  gap: 28px;  /* was: 22px */
}

.home-metric-row {
  gap: 28px;  /* was: 18px */
}

/* Description sizing */
.home-current-copy p {
  font-size: clamp(1rem, 1.5vw, 1.35rem);  /* was: clamp(1.18rem, 2vw, 1.55rem) */
}
```

---

## Files to Audit Further
- `/layouts/index.html` — Structure and content order
- `/static/site-page.css` — All hero/metrics/section styling
- `/data/home.yaml` — Content/copy that might need line breaks

---

**Status:** Audit Complete  
**Date:** August 5, 2026  
**Severity:** Medium-High (impacts professional appearance and readability)
