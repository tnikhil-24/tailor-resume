import os

# Client is built at import time; give it a dummy key so this pure-logic test runs offline.
os.environ.setdefault("GEMINI_API_KEY", "test-key")

from backend.gemini import _is_complete

RESUME = {
    "experience": [{"company": "Acme", "bullets": [{"paragraph_index": 1}, {"paragraph_index": 2}]}],
    "projects": [{"title_paragraph_index": 10}, {"title_paragraph_index": 11}],
    "skills": [{"category": "Languages"}, {"category": "Tools"}],
}


def _full_suggestions():
    return {
        "experience": [{"company": "Acme", "bullets": [{"paragraph_index": 1}, {"paragraph_index": 2}]}],
        "projects": [{"title_paragraph_index": 10}, {"title_paragraph_index": 11}],
        "skills": {"reordered_categories": [{"category": "Languages"}, {"category": "Tools"}]},
    }


def test_complete_passes():
    assert _is_complete(RESUME, _full_suggestions())


def test_dropped_bullet_fails():
    s = _full_suggestions()
    s["experience"][0]["bullets"].pop()
    assert not _is_complete(RESUME, s)


def test_dropped_project_fails():
    s = _full_suggestions()
    s["projects"].pop()
    assert not _is_complete(RESUME, s)


def test_dropped_skill_category_fails():
    s = _full_suggestions()
    s["skills"]["reordered_categories"].pop()
    assert not _is_complete(RESUME, s)
