from docx import Document
from .config import RESUME_PATH


def parse_summary() -> dict:
    doc = Document(RESUME_PATH)
    paragraphs = doc.paragraphs

    for i, para in enumerate(paragraphs):
        if para.style.name == "Heading 1" and para.text.strip().upper() == "PROFESSIONAL SUMMARY":
            for j in range(i + 1, len(paragraphs)):
                next_para = paragraphs[j]
                if next_para.style.name == "Normal" and next_para.text.strip():
                    return {"paragraph_index": j, "text": next_para.text.strip()}

    raise ValueError("Professional summary section not found in resume")
