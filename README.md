# Resume Tailor

A self-hosted tool that tailors a resume to a specific job description. It parses an existing `.docx` resume, sends each section to an LLM for rewrite/ranking suggestions, lets you accept or reject each change with a side-by-side diff, then generates a new tailored `.docx` (and optional cover letter) — while automatically logging the application to a local tracker.

## Features

- **Section-by-section AI suggestions** — rewritten summary, reworded experience bullets, reordered/expanded skills, and project relevance ranking, all shown as accept/reject diffs against the original.
- **Tone selector** — choose Concise & Technical, Results-Driven, Research-Oriented, or Startup-Focused to steer the tone of the rewritten summary.
- **Gap analysis** — flags JD keywords/skills missing from the resume.
- **Optional cover letter generation** — produces a `.txt` cover letter from the JD and your accepted resume content.
- **Change summary modal** — review everything that will change before downloading the final `.docx`.
- **Application tracker** — every generated resume is auto-logged to a local SQLite database (company, job title, JD, status, notes, date applied), with an inline-editable tracker UI.
- **Skeleton loading states** for a responsive feel while the AI processes each section.

## Tech Stack

- **Backend:** FastAPI (Python), `python-docx` for resume parsing/generation, SQLite for the application tracker.
- **Frontend:** Vanilla HTML/CSS/JS, served as static files by FastAPI.
- **AI:** Pluggable LLM provider — Google Gemini (default) or Anthropic Claude, selected via an environment variable, both using the same prompt/response contract.

## How It Works

1. The backend parses the base resume (`.docx`) into structured sections: summary, experience, skills, projects, and optional sections (research, achievements, certifications).
2. These sections plus the job description are sent to the configured LLM, which returns rewritten/reordered content and a relevance ranking for projects.
3. The frontend shows each suggestion as a diff against the original; you accept or reject individually.
4. On generate, the accepted changes are written into a copy of the original `.docx`, an optional cover letter is generated, and the application is recorded in the tracker.

## Getting Started

```bash
pip install -r requirements.txt
```

Set your LLM API key (only one is required, depending on provider):

```bash
GEMINI_API_KEY=your-key-here       # default provider
# or
ANTHROPIC_API_KEY=your-key-here
LLM_PROVIDER=claude                # to switch from the default Gemini
```

Run the app:

```bash
uvicorn backend.main:app --reload
```

The frontend is served at `http://localhost:8000`.

> **Note:** The base resume file is configured via `RESUME_PATH` in `backend/config.py`. To use your own resume, replace the `.docx` file and update that path.

## Testing

```bash
pytest
```

## License

MIT — see [LICENSE](LICENSE).
