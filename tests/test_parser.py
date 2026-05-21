from backend.parser import parse_summary, parse_experience, parse_skills, parse_projects


def test_parse_summary_returns_text_and_index():
    result = parse_summary()
    assert isinstance(result["paragraph_index"], int)
    assert isinstance(result["text"], str)
    assert len(result["text"]) > 50


def test_parse_summary_content():
    result = parse_summary()
    text = result["text"]
    assert "Software Engineer" in text or "software engineer" in text.lower()


def test_parse_experience_returns_two_roles():
    roles = parse_experience()
    assert len(roles) == 2


def test_parse_experience_companies():
    roles = parse_experience()
    companies = [r["company"] for r in roles]
    assert any("NORTH TEXAS" in c.upper() for c in companies)
    assert any("ORIANA" in c.upper() for c in companies)


def test_parse_experience_bullet_counts():
    roles = parse_experience()
    unt = next(r for r in roles if "NORTH TEXAS" in r["company"].upper())
    oriana = next(r for r in roles if "ORIANA" in r["company"].upper())
    assert len(unt["bullets"]) == 4
    assert len(oriana["bullets"]) == 5


def test_parse_experience_bullet_indices_are_ints():
    roles = parse_experience()
    for role in roles:
        for bullet in role["bullets"]:
            assert isinstance(bullet["paragraph_index"], int)
            assert isinstance(bullet["text"], str)
            assert len(bullet["text"]) > 10


def test_parse_skills_returns_eight_categories():
    skills = parse_skills()
    assert len(skills) == 8


def test_parse_skills_structure():
    skills = parse_skills()
    for s in skills:
        assert isinstance(s["paragraph_index"], int)
        assert isinstance(s["category"], str) and len(s["category"]) > 0
        assert isinstance(s["items"], list) and len(s["items"]) > 0


def test_parse_skills_known_categories():
    skills = parse_skills()
    categories = [s["category"] for s in skills]
    assert any("Programming" in c for c in categories)
    assert any("AI" in c or "ML" in c for c in categories)
    assert any("Web" in c for c in categories)


def test_parse_projects_returns_thirteen():
    projects = parse_projects()
    assert len(projects) == 13


def test_parse_projects_structure():
    projects = parse_projects()
    for p in projects:
        assert isinstance(p["title_paragraph_index"], int)
        assert isinstance(p["title"], str) and len(p["title"]) > 0
        assert isinstance(p["tech"], str)
        assert isinstance(p["bullets"], list)


def test_parse_projects_bullet_counts():
    projects = parse_projects()
    titles = {p["title"]: len(p["bullets"]) for p in projects}
    assert titles["LangGraph Stock Pattern Analyzer (FinBot)"] == 4
    assert titles["Cold Email Generator"] == 5
    assert titles["AI Creator Studio"] == 5


def test_parse_projects_title_indices_unique():
    projects = parse_projects()
    indices = [p["title_paragraph_index"] for p in projects]
    assert len(indices) == len(set(indices))
