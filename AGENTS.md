# EleutherAI Website Codex Notes

## Design workflow

For website design, layout, information architecture, homepage, navigation, research pages, community pages, staff pages, or visual polish work, use a design-first workflow even if Stella does not explicitly ask for it.

1. Start with information architecture: what belongs on this page, what belongs on a subpage, and what should be omitted.
2. Sketch the page structure before implementing. Use real section names and realistic content, not filler labels.
3. Critique the proposed structure before coding. Name what would make it feel bloated, gimmicky, thin, or hard to maintain.
4. Offer 2-3 distinct visual/layout directions when the choice is not obvious.
5. Implement only after the direction is clear, unless Stella explicitly asks for immediate edits.
6. After implementation, review the page in the browser at desktop and mobile sizes and critique spacing, hierarchy, readability, and density.
7. After every visually substantive change, regenerate the relevant preview before reporting completion: rebuild Hugo pages and refresh or start a local preview, or refresh the local tab for a standalone mockup. Give Stella the exact URL to view. Coordinate the preview port with concurrent website work before starting a server.

## Content and taste

- Do not end headings with periods.
- Prefer proof over explanation: show concrete work, people, papers, artifacts, metrics, and outcomes instead of describing the site's own structure.
- Do not add generic filler copy, meta-explanations, or decorative small labels that repeat nearby headings.
- Do not add process narration to visitor-facing copy, such as explanations of what a page is for, how its navigation works, where a link leads, or how content is maintained. Include that kind of text only when Stella explicitly asks for it or it conveys a substantial, user-relevant fact that the page would otherwise lack.
- A mockup should contain only content appropriate for the published page. Never add editorial annotations, mockup ribbons, process labels, explanatory notes, or other non-public text to the rendered design. When a necessary piece of copy is genuinely undecided, use `Lorem ipsum` as the sole placeholder rather than inventing temporary language.
- Do not invent facts, sponsored organizations, people, numbers, awards, or links. Leave structured placeholders only when they are clearly awaiting Stella's content.
- Avoid cramming every related idea onto one page. Use a hub-and-spoke structure when a topic has multiple real audiences or content types.
- Keep Hugo content/data/templates separated so Stella can edit content without digging through HTML and CSS.
- Preserve the website's shared outer content frame, border, and page gutters. Within that frame, do not put headings or prose in an additional narrower text box that causes avoidable wrapping. This includes direct `max-width` rules on text and text containers as well as indirect constraints created by narrow parent containers or grid tracks. Structured metadata columns are acceptable when they serve a clear functional purpose, but ordinary headings and prose should use the full width available inside the shared page frame.

## Project handling

- Keep exploratory design work on the active feature branch until Stella approves it.
- Do not stage or commit this `AGENTS.md` file unless Stella explicitly asks.
- When giving build instructions, include both the build command and the command or URL to open the result.
