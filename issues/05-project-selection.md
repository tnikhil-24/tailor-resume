# Issue 05: Project ranking and selection

## What to build

Extends the pipeline to cover the Project Experience section. After this slice, the output `.docx` contains only the 2-3 projects the user selected from a ranked list — all others are completely absent from the output file.

Covers all layers for the projects section:

**Parser** — extended to extract all 13 projects. Project boundary detection: a `Normal` paragraph containing `|` is a project title line. All subsequent `Normal` paragraphs until the next title line or section heading are that project's bullets. Each project yields `{ title, tech, title_paragraph_index, bullets: [{ paragraph_index, text }] }`.

**Claude Advisor** — prompt extended to include all project titles and tech stacks (bullets omitted to stay within token budget — titles + tech are sufficient for relevance scoring). Claude returns a ranked list:
```json
{
  "projects": [
    { "title": "...", "title_paragraph_index": N, "relevance_score": 0-100, "reason": "..." }
  ]
}
```
List is ordered highest score first.

**Resume Writer** — extended to delete paragraphs for every project NOT in the user's selected set. Deletion covers the title paragraph and all bullet paragraphs for that project. Selected projects remain in their original order (not re-sorted).

**Frontend** — projects section rendered as a ranked checklist. Each row shows the project title, relevance score, and Claude's reason. Checkboxes default unchecked. User selects 2-3. A counter shows how many are selected. Generate is gated until at least 1 and at most 3 projects are checked.

**Tests** — parser test extended: assert all 13 projects are extracted with correct title paragraph indices and bullet counts. Writer test extended: assert dropped project paragraphs are absent from output and kept project paragraphs are present, in original order.

## Acceptance criteria

- [ ] `POST /tailor` response includes all 13 projects ranked by relevance score
- [ ] Frontend renders the ranked checklist with score and reason per project
- [ ] Selecting 2-3 projects and generating produces a `.docx` containing only those projects
- [ ] Unselected projects are completely absent from the output (no blank lines left behind)
- [ ] Selected projects appear in their original resume order, not ranked order
- [ ] Generate is blocked if 0 projects are selected
- [ ] All prior section tailoring continues to work
- [ ] Parser and writer tests pass for the projects section

## Blocked by

[Issue 04: Skills reorder and additions](./04-skills-tailoring.md)
