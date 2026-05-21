# Issue 04: Skills reorder and additions

## What to build

Extends the pipeline to cover the Skills section. After this slice, a tailoring session produces a `.docx` with summary, experience bullets, and skills all tailored to the job description.

Covers all layers for the skills section:

**Parser** — extended to extract all 8 skill categories. Each category is a `Body Text` paragraph parsed as `Category: item, item, ...`. Parser yields a list of `{ paragraph_index, category, items }` objects.

**Claude Advisor** — prompt extended to include the full skills structure. Claude returns two things:
```json
{
  "skills": {
    "reordered_categories": [
      { "category": "...", "items": [...], "paragraph_index": N }
    ],
    "suggested_additions": [
      { "category": "...", "skill": "...", "reason": "..." }
    ]
  }
}
```
Categories are ordered by relevance to the JD. Items within each category are ordered by relevance. Suggested additions are skills found in the JD that the user confirmed they have — one confirmation prompt per addition.

**Resume Writer** — extended to rewrite each skills `Body Text` paragraph with the new category + item ordering. If the user confirmed additions, those are appended to the relevant category's item list before writing. Same invariant: only `Run.text` is modified.

**Frontend** — skills section rendered below experience. Shows a preview of the reordered skills categories. Each suggested addition shown with the category it belongs to, the skill name, and Claude's reason — Add/Skip buttons per addition. User must resolve all additions (Add or Skip) before Generate is enabled for this section.

**Tests** — parser test extended: assert all 8 categories extracted with correct items. Writer test extended: assert reordered output matches the expected category order and item order, and that confirmed additions appear in the correct category.

## Acceptance criteria

- [ ] `POST /tailor` response includes reordered skills categories and suggested additions
- [ ] Frontend renders the reordered skills preview
- [ ] Each suggested addition shows category, skill name, and reason with Add/Skip buttons
- [ ] Clicking Add includes the skill in the output; clicking Skip excludes it
- [ ] Output `.docx` skills section reflects the new category order and item order
- [ ] Confirmed additions appear appended to the correct category in the output
- [ ] Summary and experience tailoring from prior issues continue to work
- [ ] Parser and writer tests pass for the skills section

## Blocked by

[Issue 03: Experience bullet tailoring](./03-experience-tailoring.md)
