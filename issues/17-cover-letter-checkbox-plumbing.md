# 17 — Cover Letter: Checkbox + Flag Plumbing

## What to build

Add an opt-in checkbox below the tone selector pills: "Generate cover letter (.txt)". Unchecked by default. Pass `generate_cover_letter: bool` in the `/generate` POST request body. The backend receives and validates the flag but makes no extra Claude call yet (that comes in #18).

## Acceptance criteria

- [ ] Checkbox rendered below tone pills, labelled "Generate cover letter (.txt)"
- [ ] Unchecked by default
- [ ] `generate_cover_letter` bool is included in the `/generate` request body
- [ ] `/generate` endpoint accepts the flag without error
- [ ] When flag is false, behaviour is identical to today — no extra file, no extra Claude call
- [ ] When flag is true, endpoint accepts it gracefully (cover letter generation itself is #18)

## Blocked by

None — can start immediately
