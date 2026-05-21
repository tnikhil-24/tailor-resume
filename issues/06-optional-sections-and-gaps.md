# Issue 06: Optional sections, Gaps panel, and generate gate

## What to build

Final slice — completes the app. Extends the pipeline to cover the three optional sections (Research Paper, Achievements, Certifications) and adds the Gaps panel. After this slice, the full tailoring session works end-to-end: paste JD, review all sections, generate a one-page-ready `.docx`.

Covers all layers:

**Parser** — extended to extract the three optional sections:
- **Research Paper**: `Heading 1` "RESEARCH PAPER" + `List Paragraph` items
- **Achievements**: `Normal` paragraph with text "ACHIEVEMENTS" (detected by text content, not style — this heading uses `Normal` style unlike other sections) + `List Paragraph` bullets
- **Certifications**: `Heading 1` "CERTIFICATIONS" + `List Paragraph` items

Each section yields `{ heading_paragraph_index, content_paragraph_indices, texts }`.

**Claude Advisor** — prompt extended to include optional section content. Claude returns:
```json
{
  "optional_sections": {
    "research_paper":  { "keep": true/false,  "reason": "..." },
    "achievements":    { "keep": true/false,  "reason": "..." },
    "certifications":  { "keep": true/false,  "reason": "..." }
  },
  "gaps": ["skill1", "skill2", ...]
}
```
Claude is instructed to frame keep/drop recommendations around the one-page constraint and JD relevance.

**Resume Writer** — extended to delete all paragraphs (heading + content) for each dropped optional section.

**Frontend** — three optional section cards rendered below the project checklist. Each card shows Claude's recommendation (Keep/Remove badge) and reason. User can toggle to override. Gaps panel rendered at the bottom as a read-only chip list — informational only, no action required.

**Generate gate** — Generate button is enabled only when every section has been explicitly reviewed: summary accepted/rejected, all experience bullets accepted/rejected, all skill additions confirmed/skipped, at least 1 project selected, all three optional sections kept/removed.

**Tests** — parser test extended: assert all three optional sections extracted with correct paragraph indices. Writer test extended: assert dropped optional section paragraphs (including headings) are absent from output; kept sections are present and unchanged.

## Acceptance criteria

- [ ] `POST /tailor` response includes optional section recommendations and gaps list
- [ ] Each optional section card shows Claude's recommendation and reason
- [ ] Toggling keep/remove overrides Claude's default
- [ ] Dropped sections are completely absent from the output `.docx` (heading included)
- [ ] Gaps panel renders as a read-only chip list — no action buttons
- [ ] Generate button is disabled until all sections are reviewed
- [ ] Generate button becomes enabled once summary, all bullets, all skill additions, projects, and all optional sections are resolved
- [ ] Full end-to-end flow works: paste JD → review all sections → generate → open in Word → format intact
- [ ] Parser and writer tests pass for all three optional sections

## Blocked by

[Issue 05: Project ranking and selection](./05-project-selection.md)
