# 10 — Tracker: Inline Status Dropdown

## What to build

Replace the plain-text Status cell in the tracker table with an inline `<select>` dropdown. On change, fire a `PATCH /applications/{id}` request with the new status value and persist it. Options: Applied | Interviewing | Offer | Rejected.

The `PATCH` endpoint should accept a partial body — only the fields present in the request body are updated, so status and notes can share the same endpoint.

## Acceptance criteria

- [ ] `PATCH /applications/{id}` accepts `{ "status": "..." }` and updates the row
- [ ] Invalid status values return HTTP 422
- [ ] Status cell renders as a `<select>` with four options
- [ ] Current status is pre-selected on render
- [ ] Change fires PATCH immediately (no save button needed)
- [ ] UI reflects the updated value without a full page reload

## Blocked by

- #09 — Tracker Read-Only Table
