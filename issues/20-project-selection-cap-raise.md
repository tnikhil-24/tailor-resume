# 20 — Project Selection Cap Raise

## What to build

Remove the hardcoded maximum of 3 projects from the frontend validation in `app.js` and update the Claude prompt in `claude.py` to reflect the new range. New soft limit: 6 projects. The frontend counter label should update accordingly (e.g. "Select 1–6 projects").

## Acceptance criteria

- [ ] User can select up to 6 projects without hitting a validation error
- [ ] Generate button enables correctly when 1–6 projects are selected
- [ ] Counter label reads "Select 1–6 projects" (or equivalent)
- [ ] Claude prompt instructs the model that the user may keep up to 6 projects
- [ ] Selecting 0 projects still blocks generate (minimum of 1 unchanged)

## Blocked by

None — can start immediately
