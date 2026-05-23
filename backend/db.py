import sqlite3
import os
from datetime import date

_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "applications.db"))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    company               TEXT NOT NULL,
    job_title             TEXT NOT NULL,
    jd_text               TEXT NOT NULL,
    resume_filename       TEXT NOT NULL,
    cover_letter_filename TEXT,
    date_applied          TEXT NOT NULL,
    status                TEXT NOT NULL DEFAULT 'Applied',
    notes                 TEXT DEFAULT ''
)
"""


def _connect():
    return sqlite3.connect(_DB_PATH)


def init_db():
    with _connect() as conn:
        conn.execute(_SCHEMA)


def insert_application(company: str, job_title: str, jd_text: str, resume_filename: str, cover_letter_filename: str = None):
    today = date.today().strftime("%Y-%m-%d")
    with _connect() as conn:
        conn.execute(
            "INSERT INTO applications (company, job_title, jd_text, resume_filename, cover_letter_filename, date_applied) VALUES (?, ?, ?, ?, ?, ?)",
            (company, job_title, jd_text, resume_filename, cover_letter_filename, today),
        )


def get_all_applications() -> list[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY date_applied DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def update_application(id: int, **fields):
    if not fields:
        return
    cols = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [id]
    with _connect() as conn:
        conn.execute(f"UPDATE applications SET {cols} WHERE id = ?", values)
