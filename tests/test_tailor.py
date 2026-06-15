import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.main import app
from backend.parser import parse_experience, parse_skills, parse_projects

client = TestClient(app)

VALID_PAYLOAD = {
    "jd": "Looking for a Python developer with FastAPI and ML experience.",
    "job_title": "Software Engineer",
    "company": "Acme Corp",
}


@pytest.fixture(scope="module")
def suggestions():
    experience = parse_experience()
    skills = parse_skills()
    projects = parse_projects()
    return {
        "summary": {"suggested": "Tailored summary for the role."},
        "experience": [
            {
                "company": role["company"],
                "bullets": [
                    {
                        "paragraph_index": b["paragraph_index"],
                        "suggested": "Improved: " + b["text"][:40],
                        "reason": "Better keyword match",
                    }
                    for b in role["bullets"]
                ],
            }
            for role in experience
        ],
        "skills": {
            "reordered_categories": [
                {"paragraph_index": s["paragraph_index"], "category": s["category"], "items": s["items"]}
                for s in skills
            ],
            "suggested_additions": [
                {"category": "Programming Languages", "skill": "Rust", "reason": "Listed in JD"}
            ],
        },
        "projects": [
            {
                "title": p["title"],
                "title_paragraph_index": p["title_paragraph_index"],
                "relevance_score": 80,
                "reason": "Relevant to JD",
            }
            for p in projects
        ],
        "optional_sections": {
            "research_paper": {"keep": True, "reason": "Relevant"},
            "achievements": {"keep": True, "reason": "Shows impact"},
            "certifications": {"keep": False, "reason": "Not in JD"},
        },
        "gaps": ["Kubernetes", "GraphQL"],
    }


# Slice 1: valid request → 200 with all top-level keys
def test_tailor_valid_request_returns_200(suggestions):
    with patch("backend.main.get_suggestions", return_value=suggestions):
        res = client.post("/tailor", json=VALID_PAYLOAD)
    assert res.status_code == 200
    assert set(res.json().keys()) == {"summary", "experience", "skills", "projects", "optional_sections", "gaps"}


# Slice 2: validation errors
@pytest.mark.parametrize("missing_field", ["jd", "job_title", "company"])
def test_tailor_missing_required_field_returns_422(missing_field):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != missing_field}
    res = client.post("/tailor", json=payload)
    assert res.status_code == 422


def test_tailor_invalid_tone_returns_422(suggestions):
    with patch("backend.main.get_suggestions", return_value=suggestions):
        res = client.post("/tailor", json={**VALID_PAYLOAD, "tone": "Aggressive"})
    assert res.status_code == 422


# Slice 3: summary shape
def test_tailor_summary_has_required_fields(suggestions):
    with patch("backend.main.get_suggestions", return_value=suggestions):
        res = client.post("/tailor", json=VALID_PAYLOAD)
    summary = res.json()["summary"]
    assert "original" in summary
    assert "suggested" in summary
    assert "paragraph_index" in summary
    assert isinstance(summary["original"], str) and len(summary["original"]) > 0
    assert isinstance(summary["suggested"], str) and len(summary["suggested"]) > 0
    assert isinstance(summary["paragraph_index"], int)


# Slice 4: experience shape
def test_tailor_experience_companies_match_resume(suggestions):
    with patch("backend.main.get_suggestions", return_value=suggestions):
        res = client.post("/tailor", json=VALID_PAYLOAD)
    companies = [r["company"] for r in res.json()["experience"]]
    assert any("NORTH TEXAS" in c.upper() for c in companies)
    assert any("ORIANA" in c.upper() for c in companies)


def test_tailor_experience_bullets_have_all_fields(suggestions):
    with patch("backend.main.get_suggestions", return_value=suggestions):
        res = client.post("/tailor", json=VALID_PAYLOAD)
    for role in res.json()["experience"]:
        for bullet in role["bullets"]:
            assert "paragraph_index" in bullet
            assert "original" in bullet
            assert "suggested" in bullet
            assert "reason" in bullet
            assert isinstance(bullet["original"], str) and len(bullet["original"]) > 0


# Slice 5: skills shape
def test_tailor_skills_returns_all_categories(suggestions):
    with patch("backend.main.get_suggestions", return_value=suggestions):
        res = client.post("/tailor", json=VALID_PAYLOAD)
    skills = res.json()["skills"]
    assert "reordered_categories" in skills
    assert "suggested_additions" in skills
    assert len(skills["reordered_categories"]) == 8


# Slice 6: projects shape
def test_tailor_projects_have_required_fields(suggestions):
    with patch("backend.main.get_suggestions", return_value=suggestions):
        res = client.post("/tailor", json=VALID_PAYLOAD)
    for proj in res.json()["projects"]:
        assert "title" in proj
        assert "title_paragraph_index" in proj
        assert "all_paragraph_indices" in proj
        assert "relevance_score" in proj
        assert "reason" in proj
        assert isinstance(proj["all_paragraph_indices"], list)
        assert len(proj["all_paragraph_indices"]) >= 1


# Slice 7: optional sections shape
def test_tailor_optional_sections_have_required_fields(suggestions):
    with patch("backend.main.get_suggestions", return_value=suggestions):
        res = client.post("/tailor", json=VALID_PAYLOAD)
    opt = res.json()["optional_sections"]
    for key in ("research_paper", "achievements", "certifications"):
        assert key in opt
        section = opt[key]
        assert "keep" in section
        assert "reason" in section
        assert "all_paragraph_indices" in section
        assert isinstance(section["keep"], bool)
        assert isinstance(section["all_paragraph_indices"], list)
        assert len(section["all_paragraph_indices"]) >= 1


# Slice 8: gaps is a list of strings
def test_tailor_gaps_is_list_of_strings(suggestions):
    with patch("backend.main.get_suggestions", return_value=suggestions):
        res = client.post("/tailor", json=VALID_PAYLOAD)
    gaps = res.json()["gaps"]
    assert isinstance(gaps, list)
    assert all(isinstance(g, str) for g in gaps)
