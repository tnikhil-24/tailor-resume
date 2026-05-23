# PRD: Tailor-Resume — Feature & UI Expansion

## Problem Statement

The app successfully tailors resumes section-by-section, but after using it across multiple job applications the user faces three compounding problems:

1. **Lost job descriptions** — generated resumes accumulate in a folder but the JDs that produced them are gone, making it impossible to recall what was applied to or reconstruct context later.
2. **No application visibility** — there is no structured way to track which companies were applied to, when, or what stage the process is at.
3. **Output quality gaps** — the AI-generated summary often sounds generic regardless of the role type, and cover letters must be written manually from scratch.

Additionally, the UI is functional but rough: no navigation between views, no loading feedback, and no confirmation step between reviewing suggestions and downloading the final file.

---

## Solution

Add a **Job Application Tracker** that auto-captures every tailoring session into a persistent SQLite database, a **Change Summary Modal** that confirms accepted edits before download, a **Tone Selector** that steers the AI summary toward the user's target role voice, an **optional Cover Letter generator**, and a raised project selection cap. Wrap everything in a polished two-view UI with a top nav bar (Tailor | Tracker).

---

## User Stories

1. As a job applicant, I want all application data (company, job title, JD, resume filename, date) to be saved automatically when I generate a resume, so that I never lose track of what I applied to.
2. As a job applicant, I want the application status to start as "Applied" automatically, so that I don't have to set it manually every time.
3. As a job applicant, I want to update the application status (Applied / Interviewing / Offer / Rejected) inline in the tracker table without opening a separate screen, so that I can update it in one click.
4. As a job applicant, I want to add and edit notes for each application inline in the tracker table, so that I can capture context without leaving the app.
5. As a job applicant, I want to expand a tracker row to see the full job description that was used for that application, so that I can recall exactly what the role required.
6. As a job applicant, I want the date applied to auto-fill with today's date, so that I never have to type it manually.
7. As a job applicant, I want a modal after clicking Generate that lists every accepted change grouped by section, so that I can QA the output before committing to download.
8. As a job applicant, I want the Download button to live inside the change summary modal, so that review and download are explicitly linked and I cannot accidentally skip review.
9. As a job applicant, I want to select a tone preset before tailoring (Concise & Technical / Results-Driven / Research-Oriented / Startup-Focused), so that the AI-generated summary matches the voice expected by the target role.
10. As a job applicant, I want "Concise & Technical" to be the default tone, so that I don't need to make a selection for standard SWE roles.
11. As a job applicant, I want an optional cover letter checkbox on the form, so that I can request a cover letter only when I need one without extra clicks on other applications.
12. As a job applicant, I want the cover letter output as a `.txt` file saved alongside the resume, so that it is immediately available without extra steps.
13. As a job applicant, I want to select more than 3 projects in the Projects section, so that I can include more relevant work for roles that expect a richer portfolio.
14. As a job applicant, I want skeleton loaders per section card while the AI is processing, so that I have spatial feedback about what is loading rather than a generic spinner.
15. As a job applicant, I want a persistent top nav bar with Tailor and Tracker tabs as pill-style buttons, so that I can switch between tailoring a new application and reviewing past ones without losing context.
16. As a job applicant, I want the tracker to be a sortable table (not cards), so that I can scan multiple applications side-by-side efficiently.
17. As a job applicant, I want the Generate bar to have a backdrop blur, so that it does not visually cut off content beneath it.

---

## Implementation Decisions

### Navigation
- Add a persistent top nav bar with two pill-style tabs: **Tailor** (existing flow) and **Tracker** (new view).
- Active tab = green filled pill (`#2a9d5c`). Inactive = plain text.
- Single-page navigation: tab switch shows/hides the relevant view `<div>`, no page reload.

### Job Application Tracker — Database
- Use **SQLite** via Python's built-in `sqlite3` module — no new dependency.
- Single table `applications` with columns: `id`, `company`, `job_title`, `jd_text`, `resume_filename`, `cover_letter_filename` (nullable), `date_applied`, `status`, `notes`.
- Database file stored at project root as `applications.db`.
- Record inserted automatically at the end of the `/generate` endpoint after the file is written. Status defaults to `Applied`.

### Job Application Tracker — API
- `GET /applications` — returns all rows ordered by `date_applied DESC`.
- `PATCH /applications/{id}` — updates `status` and/or `notes` for a single row. Invalid status value returns 422.
- No delete endpoint (out of scope).

### Job Application Tracker — UI
- Full-width table with columns: Company | Job Title | Date Applied | Status | Notes | Resume File.
- Status cell: inline `<select>` dropdown, fires `PATCH` on change.
- Notes cell: inline editable `<input>`, fires `PATCH` on blur.
- Click company name cell → row expands below to show full JD text in a read-only `<pre>` block. Click again to collapse.
- Resume File column: filename as plain text (no download link — files are local).

### Change Summary Modal
- Triggered by the existing Generate button click — replaces the direct download trigger.
- Modal body lists accepted changes grouped by section:
  - **Summary**: one line ("Rewrite accepted")
  - **Experience**: bullet count per role ("Google — 3 bullets rewritten")
  - **Skills**: list of added skills
  - **Projects**: titles of kept projects
  - **Sections removed**: names of dropped optional sections
- "Download Resume" button inside the modal fires the `/generate` call and closes modal on success.
- If cover letter was requested, modal notes "Cover Letter: will be generated" and both files download.

### Tone Selector
- Four pill buttons rendered below the JD textarea: `Concise & Technical` (default), `Results-Driven`, `Research-Oriented`, `Startup-Focused`.
- Selected pill = green filled, unselected = outlined. Exactly one must always be selected.
- Selected tone passed as a new `tone` string field in the `/tailor` request body.
- Backend injects tone as a one-line instruction into the Claude prompt for the **summary rewrite only**. Experience bullets and other sections are unaffected.

### Cover Letter Generation
- Checkbox below tone selector pills: "Generate cover letter (.txt)". Unchecked by default.
- If unchecked: no extra Claude call, no extra file.
- If checked: second Claude call inside `/generate`, using JD + company + job title + extracted summary + experience bullets → plain-text cover letter.
- Saved as `CoverLetter_{Company}_{JobTitle}_{YYYY-MM-DD}.txt` in project root.
- `cover_letter_filename` stored in the tracker record.

### Project Selection Cap
- Remove hardcoded max of 3 from both frontend validation and backend prompt.
- New soft limit: **6 projects**. Frontend counter label updates accordingly ("Select 1–6").
- Claude prompt updated to reflect the new range.

### Loading / Skeleton State
- On Tailor button click: hide form inputs, show results container with one skeleton card per section.
- Skeleton card = gray animated gradient bars approximating each section's content shape.
- Replace skeletons with real content once `/tailor` responds.

### Visual Polish (no color scheme change)
- Refine card `box-shadow` for consistent depth.
- Standardize `border-radius` to 8px across cards, buttons, and pills.
- Add `backdrop-filter: blur(8px)` + semi-transparent background to sticky generate bar.
- Tighten typography: clear size hierarchy between section titles (`1rem` bold), labels (`0.85rem`), and body (`0.9rem`).

---

## Testing Decisions

Good tests verify external behavior through the module's public interface — not implementation details like internal query structure or loop order.

### Modules to test

**Tracker endpoints**
- `GET /applications`: returns correct JSON shape, ordered by `date_applied DESC`.
- `PATCH /applications/{id}`: status and notes update persisted correctly; invalid status value returns 422.
- `/generate` integration: after a generate call a tracker record exists with correct company, job_title, resume_filename, status=Applied, and today's date.

**Cover letter generation**
- When `generate_cover_letter=true`, a `.txt` file is written and tracker record has non-null `cover_letter_filename`.
- When `generate_cover_letter=false`, no `.txt` file is written.

**Tone injection**
- The Claude prompt for the summary section contains the selected tone string when a non-default tone is passed.

### Prior art
- Existing `pytest` suite in the project. New tests follow the same fixture and `httpx` test-client patterns already established.

---

## Out of Scope

- Multi-user support, authentication, or cloud deployment.
- Re-tailoring from a stored JD (tracker is read and status-update only).
- Inline editing of resume text in the UI.
- ATS keyword scoring.
- Multiple base resumes or resume version management.
- Deleting tracker records.
- PDF export.
- Mobile layout.

---

## Further Notes

- Recommended build order: Tracker → Change Summary Modal → Tone Selector → Cover Letter → Project cap raise → UI polish (polish can be done in parallel with any feature).
- SQLite database is local-only; no backup or sync mechanism needed.
- The Gemini fallback (existing) should also receive the `tone` parameter once it is added to the Claude path.
- Base resume path remains hardcoded in `config.py` — no upload UI needed.
