from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any
import os

from .config import RESUME_PATH
from .parser import parse_summary, parse_experience, parse_skills, parse_projects, parse_optional_sections
from .llm import get_suggestions
from .writer import generate
from .db import init_db, insert_application

app = FastAPI()


class TailorRequest(BaseModel):
    jd: str
    job_title: str
    company: str


@app.on_event("startup")
def startup():
    path = os.path.abspath(RESUME_PATH)
    assert os.path.exists(path), f"Resume not found at {path}"
    print(f"Base resume loaded: {path}")
    init_db()


class GenerateRequest(BaseModel):
    decisions: dict[str, Any]
    job_title: str
    company: str
    jd: str = ""


@app.post("/tailor")
def tailor(req: TailorRequest):
    summary = parse_summary()
    experience = parse_experience()
    skills = parse_skills()
    projects = parse_projects()
    optional_sections = parse_optional_sections()

    resume_data = {
        "summary": summary,
        "experience": experience,
        "skills": skills,
        "projects": projects,
        "optional_sections": optional_sections,
    }
    suggestions = get_suggestions(resume_data, req.jd)

    original_bullets = {
        b["paragraph_index"]: b["text"]
        for role in experience
        for b in role["bullets"]
    }

    experience_response = [
        {
            "company": role["company"],
            "bullets": [
                {
                    "paragraph_index": b["paragraph_index"],
                    "original": original_bullets.get(b["paragraph_index"], ""),
                    "suggested": b["suggested"],
                    "reason": b.get("reason", ""),
                }
                for b in role["bullets"]
            ],
        }
        for role in suggestions.get("experience", [])
    ]

    # Build project lookup: title_paragraph_index → all paragraph indices
    project_paragraphs = {
        p["title_paragraph_index"]: [p["title_paragraph_index"]] + [b["paragraph_index"] for b in p["bullets"]]
        for p in projects
    }

    projects_response = [
        {
            "title": proj["title"],
            "title_paragraph_index": proj["title_paragraph_index"],
            "all_paragraph_indices": project_paragraphs.get(proj["title_paragraph_index"], [proj["title_paragraph_index"]]),
            "relevance_score": proj.get("relevance_score", 0),
            "reason": proj.get("reason", ""),
        }
        for proj in suggestions.get("projects", [])
    ]

    # Build optional sections response — attach all_paragraph_indices for writer
    opt_suggestions = suggestions.get("optional_sections", {})
    optional_response = {}
    for key, section in optional_sections.items():
        all_indices = [section["heading_paragraph_index"]] + section["content_paragraph_indices"]
        rec = opt_suggestions.get(key, {"keep": True, "reason": ""})
        optional_response[key] = {
            "keep": rec.get("keep", True),
            "reason": rec.get("reason", ""),
            "all_paragraph_indices": all_indices,
        }

    return {
        "summary": {
            "original": summary["text"],
            "suggested": suggestions["summary"]["suggested"],
            "paragraph_index": summary["paragraph_index"],
        },
        "experience": experience_response,
        "skills": suggestions.get("skills", {"reordered_categories": [], "suggested_additions": []}),
        "projects": projects_response,
        "optional_sections": optional_response,
        "gaps": suggestions.get("gaps", []),
    }


@app.post("/generate")
def generate_resume(req: GenerateRequest):
    output_path = generate(req.decisions, req.job_title, req.company)
    filename = os.path.basename(output_path)
    insert_application(req.company, req.job_title, req.jd, filename)
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
