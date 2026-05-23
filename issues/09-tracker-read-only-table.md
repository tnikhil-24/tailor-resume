# 09 — Tracker: Read-Only Table

## What to build

Add a `GET /applications` endpoint that returns all rows from the `applications` table ordered by `date_applied DESC`. In the Tracker tab (from issue #07), replace the placeholder with a full-width table rendering those rows. Table columns: Company | Job Title | Date Applied | Status | Notes | Resume File. No inline editing in this slice — status and notes are display-only.

## Acceptance criteria

- [ ] `GET /applications` returns a JSON array of all application records, ordered by date descending
- [ ] Tracker tab renders a table with correct columns
- [ ] Table populates from the API on tab switch (or on page load)
- [ ] Empty state is shown when no applications exist ("No applications yet")
- [ ] Resume File column shows the filename as plain text (no clickable link)
- [ ] Status is shown as plain text in this slice (dropdown comes in #10)

## Blocked by

- #07 — Top Nav Bar (Tracker tab must exist)
- #08 — Tracker DB + Auto-Save (endpoint needs the DB)
