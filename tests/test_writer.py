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
