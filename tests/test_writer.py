import os
import tempfile
import pytest
from docx import Document
from docx.shared import Pt
from backend.writer import generate


def make_test_docx(summary_text: str, bold: bool = False) -> str:
    doc = Document()
    para = doc.add_paragraph()
    run = para.add_run(summary_text)
    run.bold = bold
    run.font.size = Pt(11)

    path = tempfile.mktemp(suffix=".docx")
    doc.save(path)
    return path


def test_writer_applies_accepted_summary():
    source = make_test_docx("Original summary text.")
    decisions = {"summary": {"accepted": True, "suggested": "New tailored summary.", "paragraph_index": 0}}

    output_path = generate(decisions, "SWE", "Google", source_path=source)
    try:
        result = Document(output_path)
        assert result.paragraphs[0].text == "New tailored summary."
    finally:
        os.remove(source)
        os.remove(output_path)


def test_writer_skips_rejected_summary():
    source = make_test_docx("Original summary text.")
    decisions = {"summary": {"accepted": False, "suggested": "New tailored summary.", "paragraph_index": 0}}

    output_path = generate(decisions, "SWE", "Google", source_path=source)
    try:
        result = Document(output_path)
        assert result.paragraphs[0].text == "Original summary text."
    finally:
        os.remove(source)
        os.remove(output_path)


def test_writer_preserves_run_formatting():
    source = make_test_docx("Original summary text.", bold=True)
    decisions = {"summary": {"accepted": True, "suggested": "New summary.", "paragraph_index": 0}}

    output_path = generate(decisions, "SWE", "Google", source_path=source)
    try:
        result = Document(output_path)
        run = result.paragraphs[0].runs[0]
        assert run.text == "New summary."
        assert run.bold is True
        assert run.font.size == Pt(11)
    finally:
        os.remove(source)
        os.remove(output_path)


def test_writer_applies_accepted_experience_bullet():
    doc = Document()
    doc.add_paragraph()  # paragraph 0 — summary placeholder
    para = doc.add_paragraph("Original bullet text.")
    para.style = doc.styles["List Paragraph"] if "List Paragraph" in [s.name for s in doc.styles] else doc.styles["Normal"]

    path = tempfile.mktemp(suffix=".docx")
    doc.save(path)

    decisions = {
        "experience": [{"accepted": True, "suggested": "Improved bullet.", "paragraph_index": 1}]
    }
    output_path = generate(decisions, "SWE", "Google", source_path=path)
    try:
        result = Document(output_path)
        assert result.paragraphs[1].text == "Improved bullet."
    finally:
        os.remove(path)
        os.remove(output_path)


def test_writer_skips_rejected_experience_bullet():
    doc = Document()
    doc.add_paragraph()
    doc.add_paragraph("Original bullet text.")

    path = tempfile.mktemp(suffix=".docx")
    doc.save(path)

    decisions = {
        "experience": [{"accepted": False, "suggested": "Improved bullet.", "paragraph_index": 1}]
    }
    output_path = generate(decisions, "SWE", "Google", source_path=path)
    try:
        result = Document(output_path)
        assert result.paragraphs[1].text == "Original bullet text."
    finally:
        os.remove(path)
        os.remove(output_path)


def test_writer_reorders_skills():
    doc = Document()
    p0 = doc.add_paragraph()
    p0.add_run("Web Development: React, Node")
    p1 = doc.add_paragraph()
    p1.add_run("AI/ML: LangChain, RAG")

    path = tempfile.mktemp(suffix=".docx")
    doc.save(path)

    decisions = {
        "skills": {
            "reordered_categories": [
                {"paragraph_index": 1, "category": "AI/ML", "items": ["RAG", "LangChain"]},
                {"paragraph_index": 0, "category": "Web Development", "items": ["Node", "React"]},
            ],
            "additions": [],
        }
    }
    output_path = generate(decisions, "SWE", "Google", source_path=path)
    try:
        result = Document(output_path)
        assert result.paragraphs[0].text == "AI/ML: RAG, LangChain"
        assert result.paragraphs[1].text == "Web Development: Node, React"
    finally:
        os.remove(path)
        os.remove(output_path)


def test_writer_appends_confirmed_addition():
    doc = Document()
    p = doc.add_paragraph()
    p.add_run("AI/ML: LangChain, RAG")

    path = tempfile.mktemp(suffix=".docx")
    doc.save(path)

    decisions = {
        "skills": {
            "reordered_categories": [
                {"paragraph_index": 0, "category": "AI/ML", "items": ["LangChain", "RAG"]},
            ],
            "additions": [{"category": "AI/ML", "skill": "PyTorch", "added": True}],
        }
    }
    output_path = generate(decisions, "SWE", "Google", source_path=path)
    try:
        result = Document(output_path)
        assert "PyTorch" in result.paragraphs[0].text
    finally:
        os.remove(path)
        os.remove(output_path)


def test_writer_does_not_modify_base():
    source = make_test_docx("Original summary text.")
    original_mtime = os.path.getmtime(source)
    decisions = {"summary": {"accepted": True, "suggested": "New summary.", "paragraph_index": 0}}

    output_path = generate(decisions, "SWE", "Google", source_path=source)
    try:
        assert os.path.getmtime(source) == original_mtime
        source_doc = Document(source)
        assert source_doc.paragraphs[0].text == "Original summary text."
    finally:
        os.remove(source)
        os.remove(output_path)
