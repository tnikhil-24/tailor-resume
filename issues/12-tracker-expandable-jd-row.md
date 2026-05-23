# 12 — Tracker: Expandable JD Row

## What to build

Make the Company name cell in the tracker table clickable. Clicking it toggles an expanded row beneath the application row that displays the full `jd_text` in a read-only `<pre>` block. Clicking again collapses it. Only one row can be expanded at a time.

## Acceptance criteria

- [ ] Company name cell is visually clickable (cursor pointer, subtle underline or highlight)
- [ ] Click expands a row beneath showing full JD text in a `<pre>` block
- [ ] Click again collapses the expanded row
- [ ] Expanding a second row collapses any currently open row
- [ ] JD text is read-only (no editing)
- [ ] Works correctly for all rows including the most recently added

## Blocked by

- #09 — Tracker Read-Only Table
