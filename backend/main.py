from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from .config import RESUME_PATH

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


@app.post("/tailor")
def tailor(req: TailorRequest):
    print(f"Received: company={req.company!r} job_title={req.job_title!r} jd_length={len(req.jd)}")
    return {"company": req.company, "job_title": req.job_title, "jd": req.jd}


frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
