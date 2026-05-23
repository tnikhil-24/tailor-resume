# 08 — Tracker: DB Schema + Auto-Save on Generate

## What to build

Create a new `db.py` backend module that initialises a local SQLite database (`applications.db` at project root) and exposes functions to insert and query application records. At the end of the existing `/generate` endpoint, automatically insert a record using the data already available in the request (company, job title, JD text, resume filename, today's date). Status defaults to `Applied`.

No UI or new API endpoints in this slice — verifiable by inspecting `applications.db` after a generate call.

Schema:

```
applications(
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  company          TEXT NOT NULL,
  job_title        TEXT NOT NULL,
  jd_text          TEXT NOT NULL,
  resume_filename  TEXT NOT NULL,
  cover_letter_filename TEXT,        -- nullable, populated later
  date_applied     TEXT NOT NULL,    -- ISO date string YYYY-MM-DD
  status           TEXT NOT NULL DEFAULT 'Applied',
  notes            TEXT DEFAULT ''
)
```

## Acceptance criteria

- [ ] `applications.db` is created at project root on first run if it does not exist
- [ ] Every successful `/generate` call inserts one row with correct company, job_title, jd_text, resume_filename, date_applied (today), status=Applied
- [ ] Failed generate calls do not insert a partial record
- [ ] `db.py` exposes at minimum: `init_db()`, `insert_application(...)`, `get_all_applications()`, `update_application(id, **fields)`

## Blocked by

None — can start immediately
