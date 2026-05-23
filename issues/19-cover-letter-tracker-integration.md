# 19 — Cover Letter: Tracker Integration

## What to build

When a cover letter is generated, store its filename in the `cover_letter_filename` column of the tracker record created in #08. The tracker table (from #09) should display the cover letter filename in a new column or as a secondary line under the Resume File column.

## Acceptance criteria

- [ ] `cover_letter_filename` is populated in the DB record when `generate_cover_letter=true`
- [ ] `cover_letter_filename` is NULL in the DB record when `generate_cover_letter=false`
- [ ] Tracker table shows cover letter filename (or a dash if none) alongside resume filename
- [ ] `GET /applications` response includes `cover_letter_filename` field

## Blocked by

- #08 — Tracker: DB Schema + Auto-Save (cover_letter_filename column)
- #18 — Cover Letter: Claude Call + .txt Output (filename is available to store)
