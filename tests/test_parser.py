from backend.parser import parse_summary


def test_parse_summary_returns_text_and_index():
    result = parse_summary()
    assert isinstance(result["paragraph_index"], int)
    assert isinstance(result["text"], str)
    assert len(result["text"]) > 50


def test_parse_summary_content():
    result = parse_summary()
    # Known keywords from the actual resume summary
    text = result["text"]
    assert "Software Engineer" in text or "software engineer" in text.lower()
