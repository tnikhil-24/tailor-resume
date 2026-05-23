# 15 — Tone Selector: Form + API Plumbing

## What to build

Add four pill-style tone buttons below the JD textarea in the form: **Concise & Technical** (default selected), **Results-Driven**, **Research-Oriented**, **Startup-Focused**. Exactly one pill is always selected. Pass the selected tone as a `tone` string field in the `/tailor` POST request body. The backend receives and validates the field but does not use it yet (prompt injection comes in #16).

## Acceptance criteria

- [ ] Four tone pills rendered below the JD textarea
- [ ] "Concise & Technical" is selected by default on page load
- [ ] Clicking a pill deselects the previous and selects the new one
- [ ] Selected pill = green filled; unselected = outlined
- [ ] `tone` value is included in the `/tailor` request body
- [ ] `/tailor` endpoint accepts and validates the `tone` field (unknown values return 422)
- [ ] Existing tailoring behaviour is unchanged when tone = "Concise & Technical"

## Blocked by

None — can start immediately
