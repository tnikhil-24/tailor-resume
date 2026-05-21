from docx import Document
from .config import RESUME_PATH


def _load() -> list:
    return Document(RESUME_PATH).paragraphs


def parse_summary() -> dict:
    paragraphs = _load()
    for i, para in enumerate(paragraphs):
        if para.style.name == "Heading 1" and para.text.strip().upper() == "PROFESSIONAL SUMMARY":
            for j in range(i + 1, len(paragraphs)):
                p = paragraphs[j]
                if p.style.name == "Normal" and p.text.strip():
                    return {"paragraph_index": j, "text": p.text.strip()}
    raise ValueError("Professional summary section not found in resume")


def parse_skills() -> list:
    paragraphs = _load()

    start = next(
        (i for i, p in enumerate(paragraphs)
         if p.style.name == "Heading 1" and p.text.strip().upper() == "SKILLS"),
        None,
    )
    if start is None:
        raise ValueError("Skills section not found in resume")

    skills = []
    for i in range(start + 1, len(paragraphs)):
        para = paragraphs[i]
        if para.style.name == "Heading 1":
            break
        if para.style.name == "Body Text" and para.text.strip():
            text = para.text.strip()
            if ":" in text:
                category, _, items_str = text.partition(":")
                items = [item.strip() for item in items_str.split(",") if item.strip()]
                skills.append({"paragraph_index": i, "category": category.strip(), "items": items})

    return skills


def parse_projects() -> list:
    paragraphs = _load()

    start = next(
        (i for i, p in enumerate(paragraphs)
         if p.style.name == "Heading 1" and p.text.strip().upper() == "PROJECT EXPERIENCE"),
        None,
    )
    if start is None:
        raise ValueError("Project experience section not found in resume")

    projects = []
    current_project = None

    for i in range(start + 1, len(paragraphs)):
        para = paragraphs[i]
        text = para.text.strip()

        if para.style.name == "Heading 1":
            break
        if para.style.name == "Normal" and text and "|" in text:
            parts = text.split("|", 1)
            current_project = {
                "title": parts[0].strip(),
                "tech": parts[1].strip() if len(parts) > 1 else "",
                "title_paragraph_index": i,
                "bullets": [],
            }
            projects.append(current_project)
        elif para.style.name == "Normal" and text and current_project:
            current_project["bullets"].append({"paragraph_index": i, "text": text})

    return projects


def parse_experience() -> list:
    paragraphs = _load()

    start = next(
        (i for i, p in enumerate(paragraphs)
         if p.style.name == "Heading 1" and p.text.strip().upper() == "WORK EXPERIENCE"),
        None,
    )
    if start is None:
        raise ValueError("Work experience section not found in resume")

    roles = []
    current_role = None
    role_title_found = False

    for i in range(start + 1, len(paragraphs)):
        para = paragraphs[i]
        style = para.style.name
        text = para.text.strip()

        if style == "Heading 1":
            break
        if style == "Heading 2" and text:
            current_role = {"company": text, "bullets": []}
            role_title_found = False
            roles.append(current_role)
        elif style == "Normal" and text and current_role and not role_title_found:
            role_title_found = True  # skip role/dates line — not tailored
        elif style == "List Paragraph" and text and current_role:
            current_role["bullets"].append({"paragraph_index": i, "text": text})

    return roles
