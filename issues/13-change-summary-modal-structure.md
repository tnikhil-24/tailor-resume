# 13 — Change Summary Modal: Structure

## What to build

Intercept the Generate button click in `app.js`. Instead of immediately firing `/generate`, show a modal that summarises every accepted change grouped by section. The modal has no Download button yet — this slice is about structure and content only.

Sections to display in the modal:
- **Summary**: "Rewrite accepted" (or "Original kept" if rejected)
- **Experience**: per-role bullet count ("Google — 3 bullets rewritten, 1 kept original")
- **Skills**: list of skill additions accepted (or "None added")
- **Projects**: titles of selected projects
- **Sections removed**: names of dropped optional sections (or "None removed")

Modal can be dismissed with an X or clicking the backdrop.

## Acceptance criteria

- [ ] Generate button click opens a modal instead of triggering download
- [ ] Modal shows accepted changes grouped by the five section categories above
- [ ] Counts and titles are derived from the current `state` object (no extra API call)
- [ ] Modal can be closed via X button and backdrop click
- [ ] Closing the modal does not reset any review decisions
- [ ] Modal is accessible (focus trapped inside while open, closes on Escape)

## Blocked by

None — can start immediately
