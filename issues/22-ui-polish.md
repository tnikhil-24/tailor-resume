# 22 — UI Polish

## What to build

Tighten the visual quality of the existing UI in `style.css` without changing the color scheme. Four targeted improvements:

1. **Backdrop blur on generate bar** — add `backdrop-filter: blur(8px)` + semi-transparent background so content scrolling beneath it doesn't feel cut off
2. **Consistent border-radius** — standardise to `8px` across all cards, buttons, and pills
3. **Refined card shadows** — replace flat or heavy shadows with a consistent subtle `box-shadow` (e.g. `0 1px 4px rgba(0,0,0,0.08)`)
4. **Typography hierarchy** — section titles at `1rem` bold, labels at `0.85rem`, body text at `0.9rem`; consistent `line-height` throughout

No color scheme changes. No layout changes.

## Acceptance criteria

- [ ] Generate bar has backdrop blur and does not feel like it cuts content off
- [ ] All cards, buttons, and pills use `border-radius: 8px` consistently
- [ ] Card shadows are uniform and subtle across all section cards
- [ ] Typography scale is consistent: section titles, labels, and body text are visually distinct
- [ ] No existing functionality is broken by CSS changes
- [ ] Polish applies to both Tailor and Tracker views

## Blocked by

- #07 — Top Nav Bar (so polish applies to the final nav layout too)
