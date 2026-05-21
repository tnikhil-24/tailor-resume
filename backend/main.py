from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any
import os

from .config import RESUME_PATH
from .parser import parse_summary, parse_experience
from .claude import get_suggestions
from .writer import generate

app = FastAPI()


class TailorRequest(BaseModel):
    jd: str
    job_title: str
    company: str


@app.on_event("startup")
def check_resume():
    path = os.path.abspath(RESUME_PATH)
    assert os.path.exists(path), f"Resume not found at {path}"
    print(f"Base resume loaded: {path}")


class GenerateRequest(BaseModel):
    decisions: dict[str, Any]
    job_title: str
    company: str


@app.post("/tailor")
def tailor(req: TailorRequest):
    summary = parse_summary()
    experience = parse_experience()

    resume_data = {"summary": summary, "experience": experience}
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

    return {
        "summary": {
            "original": summary["text"],
            "suggested": suggestions["summary"]["suggested"],
            "paragraph_index": summary["paragraph_index"],
        },
        "experience": experience_response,
    }


@app.post("/generate")
def generate_resume(req: GenerateRequest):
    output_path = generate(req.decisions, req.job_title, req.company)
    filename = os.path.basename(output_path)
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
