# PRD: Resume Tailor App

## Problem Statement

When tailoring a resume for a specific job, sharing the `.docx` file with an AI assistant causes the formatting to be altered — fonts, spacing, styles, and layout change in ways that require manual correction. The current workaround is to manually edit the resume in Microsoft Word per job application, which is slow and error-prone. There is no structured way to see what changed, why it changed, or to selectively accept only the suggestions that make sense.

---

## Solution

A local web application that accepts a pasted job description and produces a new, tailored `.docx` resume file. The base resume is fixed in the app — no repeated uploads. Claude analyzes the job description against the resume and returns structured suggestions across all relevant sections. The user reviews each suggestion in an inline diff UI (red/green, word-level), accepts or rejects per bullet/section, then clicks one button to generate the tailored output file. The base resume is never modified.

---

## User Stories

1. As a job applicant, I want to paste a job description into the app, so that Claude can analyze it against my resume.
2. As a job applicant, I want the app to use my fixed base resume without uploading it every time, so that I can start tailoring immediately.
3. As a job applicant, I want Claude to rewrite my professional summary targeting the job description, so that my opening pitch matches the role.
4. As a job applicant, I want to see the original and suggested summary side-by-side as an inline word-level diff, so that I can evaluate exactly what changed.
5. As a job applicant, I want to accept or reject the professional summary rewrite in one click, so that I stay in control of my narrative.
6. As a job applicant, I want Claude to reorder my skills categories by relevance to the JD, so that the most relevant skills appear first for ATS scanners and recruiters.
7. As a job applicant, I want Claude to reorder skills within each category by relevance to the JD, so that the most relevant individual skills surface first.
8. As a job applicant, I want Claude to flag skills mentioned in the JD that are not in my resume, so that I can decide whether to add them.
9. As a job applicant, I want to confirm or skip each suggested skill addition individually, so that I never add a skill I don't actually have.
10. As a job applicant, I want Claude to suggest inline rewrites for each experience bullet point, so that my work history uses the language and keywords from the JD.
11. As a job applicant, I want to see each experience bullet as a word-level red/green diff, so that I can evaluate the suggestion at a glance.
12. As a job applicant, I want to accept or reject each experience bullet rewrite independently, so that I can mix good suggestions with my original phrasing.
13. As a job applicant, I want Claude to rank all 13+ projects by relevance to the job description with a score and reason, so that I know which projects to highlight.
14. As a job applicant, I want to see the full ranked project list and select 2-3 to keep, so that I can override Claude's recommendation if I disagree.
15. As a job applicant, I want unselected projects to be completely absent from the output file, so that the tailored resume is clean and focused.
16. As a job applicant, I want Claude to recommend whether to keep or drop the Research Paper section per job, so that I don't waste space on irrelevant academic work.
17. As a job applicant, I want Claude to recommend whether to keep or drop the Achievements section per job, so that the resume stays tight for roles that don't value it.
18. As a job applicant, I want Claude to recommend whether to keep or drop the Certifications section per job, so that only relevant credentials appear.
19. As a job applicant, I want to override Claude's keep/drop recommendation for each optional section, so that I always have final say.
20. As a job applicant, I want to see a read-only Gaps panel listing JD keywords not found anywhere in my resume, so that I can prepare for interview questions on those topics.
21. As a job applicant, I want to click a single "Generate Tailored Resume" button after reviewing all suggestions, so that the output is produced only when I'm satisfied.
22. As a job applicant, I want the output file named with the company and role (e.g. `Resume_Google_SWE_2026-05-21.docx`), so that I can identify it instantly in my file system.
23. As a job applicant, I want the output `.docx` to be formatting-identical to my base resume, so that I can open it in Word and export to PDF without any cleanup.
24. As a job applicant, I want the base resume file to never be modified, so that I always have a clean source of truth to start from.
25. As a job applicant, I want the app to run locally with no login or cloud dependency, so that my resume and job data stay private.

---

## Implementation Decisions

### Module Breakdown

**1. Resume Parser**
Reads the fixed base `.docx` and produces a structured in-memory representation of all 9 sections with paragraph indices. Paragraph indices are the stable reference used throughout the pipeline — every downstream module refers to content by index, not by text search.

Sections and their detection strategy:
- **Header**: paragraphs 0–1 (Title + Normal style), always skipped
- **Professional Summary**: first `Heading 1` followed by `Normal` paragraph
- **Skills**: `Heading 1` "SKILLS" followed by `Body Text` paragraphs; each line parsed as `Category: item, item, ...`
- **Work Experience**: `Heading 1` "WORK EXPERIENCE" followed by `Heading 2` (company), `Normal` (role/dates), `List Paragraph` (bullets)
- **Research Paper**: `Heading 1` "RESEARCH PAPER" followed by `List Paragraph` items
- **Project Experience**: `Heading 1` "PROJECT EXPERIENCE" followed by `Normal` paragraphs; project boundary detected by presence of `|` separator in title line
- **Education**: `Heading 1` "EDUCATION" followed by `Heading 2` + `Body Text` + `Normal`; always skipped by writer
- **Achievements**: `Normal` paragraph with text "ACHIEVEMENTS" (not Heading 1) followed by `List Paragraph` bullets
- **Certifications**: `Heading 1` "CERTIFICATIONS" followed by `List Paragraph` items

**2. Claude Advisor**
Takes the parsed resume dict and the raw job description text. Makes a single Claude API call and returns a structured JSON response covering all tailoring suggestions. Uses `claude-sonnet-4-6`. Prompt instructs Claude to return only valid JSON matching the agreed contract — no prose, no markdown wrapping.

Claude JSON response shape:
```
{
  "summary": { "suggested": "..." },
  "skills": {
    "reordered_categories": [
      { "category": "...", "items": [...], "paragraph_index": N }
    ],
    "suggested_additions": [
      { "category": "...", "skill": "...", "reason": "..." }
    ]
  },
  "experience": [
    {
      "company": "...",
      "bullets": [
        { "paragraph_index": N, "suggested": "...", "reason": "..." }
      ]
    }
  ],
  "projects": [
    { "title": "...", "title_paragraph_index": N, "relevance_score": 0-100, "reason": "..." }
  ],
  "optional_sections": {
    "research_paper": { "keep": true/false, "reason": "..." },
    "achievements":   { "keep": true/false, "reason": "..." },
    "certifications": { "keep": true/false, "reason": "..." }
  },
  "gaps": ["skill1", "skill2", ...]
}
```

**3. Resume Writer**
Takes the original `.docx` and a `decisions` payload (the accepted subset of Claude's suggestions). Produces a new `.docx` without touching the original.

Write operations, in order:
1. Replace text runs in the summary paragraph (paragraph index 3) — never touch run formatting
2. Rewrite each skills `Body Text` paragraph text in the new category/item order
3. Replace text runs in accepted experience bullets
4. Delete paragraphs for unselected projects (title paragraph + all bullet paragraphs up to the next title or section heading)
5. Delete all paragraphs for each dropped optional section (heading + content paragraphs)

Key invariant: only `.text` on `Run` objects is ever modified. No style, font, size, spacing, or paragraph formatting is touched.

**4. FastAPI Backend**
Two endpoints:
- `POST /tailor` — accepts `{ jd: string, job_title: string, company: string }`, returns Claude suggestions JSON
- `POST /generate` — accepts `{ decisions: object, job_title: string, company: string }`, returns `.docx` file as a download

Base resume path is read from `config.py` at startup. No file upload surface.

**5. Vanilla JS Frontend**
Single-page app. Sections rendered in order after `/tailor` responds:
- **Summary**: full paragraph inline diff, Accept/Reject
- **Skills**: reordered preview table, per-skill Add/Skip for additions
- **Experience**: per-bullet inline diff (red strikethrough + green insertion), Accept/Reject
- **Projects**: ranked checklist with score and reason, checkbox per project
- **Research Paper / Achievements / Certifications**: keep/remove toggle with Claude's reason shown
- **Gaps**: read-only chip list
- **Generate button**: enabled only after all sections have been reviewed; triggers `/generate` and triggers file download

Word-level diff rendering uses `diff-match-patch` JS library applied per bullet/summary.

### Architectural Decisions

- **Single Claude call per tailoring session** — all sections in one prompt. Avoids multiple round-trips and keeps latency low.
- **Paragraph index as stable reference** — the parser assigns indices once; writer uses them directly. No fragile text-matching lookups.
- **Base resume never opened for writing** — writer always calls `Document(base_path)` to get a fresh copy, then saves to a new path.
- **Output filename convention**: `Resume_{Company}_{JobTitle}_{YYYY-MM-DD}.docx`
- **Config over UI for base resume path** — proficient user sets `RESUME_PATH` in `config.py` once. No upload UI needed in v1.

---

## Testing Decisions

**What makes a good test here**: test the external behavior of each module given realistic inputs. Do not test internal parsing implementation details (e.g. which loop structure is used). Test that given a known `.docx`, the parser produces the expected shape; given a known decisions payload, the writer produces a `.docx` with the expected text changes and format preservation.

**Modules to test:**

- **Parser**: given the actual base resume `.docx`, assert that all sections are extracted with correct paragraph indices, correct bullet counts per project, and correct skills structure. This is the highest-value test since the parser is the foundation everything else depends on.

- **Writer**: given a minimal synthetic `.docx` and a decisions payload, assert (a) accepted bullet text is changed, (b) rejected bullet text is unchanged, (c) dropped project paragraphs are absent, (d) kept project paragraphs are present, (e) run-level formatting (bold, font size) is identical between input and output for modified paragraphs. Format preservation is the core product guarantee — this must be tested explicitly.

- **Claude Advisor**: not unit-tested (external API). Validated manually during Step 2 of the build with a real JD and spot-checked for JSON shape validity.

- **FastAPI endpoints**: integration-tested with `httpx` test client. `/tailor` mocked at the Claude boundary. `/generate` tested with a real decisions payload against the actual base resume.

---

## Out of Scope

- Uploading a different base resume (v2 feature)
- Multi-resume management or version history
- PDF export (user does this manually in Word — existing workflow preserved)
- Hosted/cloud deployment
- Authentication or user accounts
- Editing the resume content directly within the app
- Auto-fitting content to exactly one page (app gives Claude the tools, user makes the final call)

---

## Further Notes

- The Achievements section uses `Normal` paragraph style for its heading (not `Heading 1` like other sections) — the parser must detect it by text content, not style.
- Projects use `Normal` style for both title lines and bullet lines — project boundary detection relies on the `|` character in the title line, not on style changes.
- The base resume currently has 13 projects. Project selection target is 2-3 per tailored output.
- The one-page constraint is the driving motivation for optional section dropping and project trimming — Claude's recommendations should be framed around this constraint in the prompt.
