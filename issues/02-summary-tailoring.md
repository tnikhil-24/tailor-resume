# Issue 02: Professional Summary tailoring — first demoable slice

## What to build

First fully working end-to-end slice. The user pastes a job description, clicks Tailor, sees an inline word-level diff of their professional summary, accepts or rejects it, clicks Generate, and downloads a new `.docx` with the change applied. The base resume is never modified.

Covers all layers for the summary section:

**Parser** — extracts the professional summary paragraph and its index from the base `.docx`. Summary is identified as the `Normal` paragraph immediately following the `Heading 1` "PROFESSIONAL SUMMARY".

**Claude Advisor** — sends the summary text + job description to Claude (`claude-sonnet-4-6`) in a single API call. Returns structured JSON:
```json
{ "summary": { "suggested": "..." } }
```
Prompt instructs Claude to return only valid JSON — no prose, no markdown wrapping.

**Resume Writer** — accepts a decisions payload, opens a fresh copy of the base `.docx`, replaces only the text runs in the summary paragraph, and saves to a new file. Run-level formatting (bold, font size, color) is never touched. Key invariant: only `Run.text` is modified.

**FastAPI** — `POST /tailor` calls parser + Claude Advisor, returns suggestions JSON. `POST /generate` calls writer with the decisions payload, returns the `.docx` as a file download named `Resume_{Company}_{JobTitle}_{YYYY-MM-DD}.docx`.

**Frontend** — renders the summary section with a word-level inline diff (red strikethrough for removed words, green for added) using `diff-match-patch`. Accept/Reject buttons. Generate button triggers `/generate` and initiates file download.

**Tests** — parser test: given the base resume, assert summary text and paragraph index are correctly extracted. Writer test: given a decisions payload with a new summary, assert the output `.docx` summary text changed and run-level formatting is identical to the input.

## Acceptance criteria

- [ ] `POST /tailor` returns `{ "summary": { "original": "...", "suggested": "..." } }`
- [ ] Frontend renders a word-level red/green diff for the summary
- [ ] Accepting the summary and clicking Generate downloads a `.docx`
- [ ] Rejecting the summary and clicking Generate downloads a `.docx` with the original summary unchanged
- [ ] Output file is named `Resume_{Company}_{JobTitle}_{YYYY-MM-DD}.docx`
- [ ] Opening the output in Word shows formatting identical to the base resume
- [ ] Base resume file is not modified at any point
- [ ] Parser test passes against the actual base `.docx`
- [ ] Writer format-preservation test passes

## Blocked by

[Issue 01: Bare-bones pipeline scaffold](./01-scaffold.md)
