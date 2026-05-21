import os
from datetime import date
from docx import Document
from .config import RESUME_PATH

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def generate(decisions: dict, job_title: str, company: str, source_path: str = None) -> str:
    source = source_path or os.path.abspath(RESUME_PATH)
    doc = Document(source)

    summary = decisions.get("summary", {})
    if summary.get("accepted") and summary.get("suggested"):
        para = doc.paragraphs[summary["paragraph_index"]]
        runs = para.runs
        if runs:
            runs[0].text = summary["suggested"]
            for run in runs[1:]:
                run.text = ""
        else:
            para.add_run(summary["suggested"])

    today = date.today().strftime("%Y-%m-%d")
    safe_company = company.strip().replace(" ", "_")
    safe_title = job_title.strip().replace(" ", "_")
    filename = f"Resume_{safe_company}_{safe_title}_{today}.docx"
    output_path = os.path.join(_PROJECT_ROOT, filename)

    doc.save(output_path)
    return output_path
