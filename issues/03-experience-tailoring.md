# Issue 03: Experience bullet tailoring

## What to build

Extends the working pipeline from Issue 02 to cover the Work Experience section. After this slice, a single tailoring session produces a `.docx` with both the professional summary and experience bullets tailored to the job description.

Covers all layers for the experience section:

**Parser** — extended to extract both work experience roles (University of North Texas and Oriana Software Solutions). Each role yields a list of bullets with paragraph indices. Experience entries are identified by `Heading 2` (company name), followed by a `Normal` paragraph (role/dates), followed by `List Paragraph` bullets.

**Claude Advisor** — prompt extended to include experience bullets. Claude returns suggestions for each bullet:
```json
{
  "experience": [
    {
      "company": "...",
      "bullets": [
        { "paragraph_index": N, "suggested": "...", "reason": "..." }
      ]
    }
  ]
}
```

**Resume Writer** — extended to replace text runs in accepted experience bullets. Rejected bullets are left untouched. Same invariant: only `Run.text` is modified, never formatting.

**FastAPI** — `/tailor` and `/generate` extended to pass experience suggestions through and apply accepted bullet decisions.

**Frontend** — experience section rendered below the summary. Each role shown as a labeled group. Each bullet rendered as a word-level red/green diff with Accept/Reject. Accepted/rejected state tracked per bullet independently.

**Tests** — parser test extended: assert correct bullet count per role and correct paragraph indices. Writer test extended: assert accepted bullets are changed, rejected bullets are unchanged, formatting is preserved.

## Acceptance criteria

- [ ] `POST /tailor` response includes experience suggestions for both roles
- [ ] Each experience bullet renders as an independent word-level diff in the frontend
- [ ] Accepting a bullet and generating downloads a `.docx` with that bullet changed
- [ ] Rejecting a bullet leaves it unchanged in the output
- [ ] Accepting some bullets and rejecting others in the same role works correctly
- [ ] Summary tailoring from Issue 02 continues to work alongside experience tailoring
- [ ] Parser and writer tests pass for the experience section

## Blocked by

[Issue 02: Professional Summary tailoring](./02-summary-tailoring.md)
