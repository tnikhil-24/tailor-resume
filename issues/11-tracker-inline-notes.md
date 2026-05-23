# 11 — Tracker: Inline Notes Field

## What to build

Replace the plain-text Notes cell in the tracker table with an inline `<input type="text">`. On blur, fire `PATCH /applications/{id}` with the updated notes value and persist it. The PATCH endpoint from #10 already handles partial updates — notes just needs to be wired in.

## Acceptance criteria

- [ ] Notes cell renders as an `<input>` field pre-filled with current notes value
- [ ] Blur fires `PATCH /applications/{id}` with `{ "notes": "..." }`
- [ ] Empty notes are saved as an empty string (not null)
- [ ] Input does not submit on Enter — only blur triggers save
- [ ] No full page reload needed after save

## Blocked by

- #09 — Tracker Read-Only Table
