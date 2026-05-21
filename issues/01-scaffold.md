# Issue 01: Bare-bones pipeline scaffold

## What to build

Set up the full project structure so the local web app runs end-to-end with no logic yet. A user opens the browser, pastes a job description, clicks Tailor, and the backend receives and echoes it back. Nothing useful yet — this proves the pipe runs locally before any real work begins.

Covers:
- Project folder structure (`backend/`, `frontend/`)
- `config.py` with `RESUME_PATH` pointing at the base `.docx`
- FastAPI app with a `POST /tailor` stub that echoes the request body
- Static file serving for the frontend from FastAPI
- `index.html` with a JD textarea, job title field, company field, and Tailor button
- `app.js` that POSTs to `/tailor` and logs the response to the console
- `requirements.txt` with `fastapi`, `uvicorn`, `python-docx`, `anthropic`

## Acceptance criteria

- [ ] Running `uvicorn backend.main:app` starts the server without errors
- [ ] Opening `http://localhost:8000` serves the frontend HTML
- [ ] Clicking Tailor POSTs `{ jd, job_title, company }` to `/tailor` and the backend logs the received payload
- [ ] `config.py` contains `RESUME_PATH` and the app reads it at startup without error
- [ ] `Nikhil_Resume - Copy.docx` is NOT in `.gitignore` (it is the tracked base resume)
- [ ] `Resume_*.docx` IS in `.gitignore` (output files are not tracked)

## Blocked by

None — can start immediately.
