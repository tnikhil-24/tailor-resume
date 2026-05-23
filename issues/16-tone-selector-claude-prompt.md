# 16 — Tone Selector: Claude Prompt Injection

## What to build

In `claude.py`, inject the selected tone as a one-line instruction into the summary rewrite section of the Claude prompt. Only the summary rewrite is affected — experience bullets, skills, projects, and all other sections are unchanged.

Tone instruction examples (exact wording can be tuned):
- Results-Driven: "Write the summary to emphasise measurable impact and quantifiable outcomes."
- Research-Oriented: "Write the summary to highlight academic rigour, publications, and research contributions."
- Startup-Focused: "Write the summary to convey ownership, scrappiness, and ability to operate in ambiguous fast-moving environments."
- Concise & Technical: no extra instruction (default behaviour, no change to prompt).

The Gemini fallback in `gemini.py` should also receive the same injection.

## Acceptance criteria

- [ ] Non-default tone values inject the corresponding one-line instruction into the summary prompt section
- [ ] Default tone ("Concise & Technical") leaves the prompt unchanged
- [ ] Experience bullets and all other sections are unaffected by tone
- [ ] Gemini fallback applies the same injection

## Blocked by

- #15 — Tone Selector: Form + API Plumbing
