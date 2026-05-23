# 21 — Skeleton Loaders

## What to build

On Tailor button click, instead of showing a generic spinner, hide the form inputs and show one animated skeleton card per section (Summary, Experience, Skills, Projects, Optional Sections, Gaps). Each skeleton approximates the shape of that section's content using gray animated gradient bars. Replace all skeleton cards with real content once the `/tailor` response arrives.

## Acceptance criteria

- [ ] Tailor button click hides the form and shows 6 skeleton cards
- [ ] Each skeleton card has a header placeholder and 2–4 content bar placeholders sized to match the real section
- [ ] Skeleton bars animate with a shimmer/gradient sweep effect
- [ ] All skeletons are replaced atomically with real section content when `/tailor` responds
- [ ] On error, skeletons are removed and an error message is shown
- [ ] Form is restored (not the skeletons) if the user navigates to Tracker tab and back

## Blocked by

None — can start immediately
