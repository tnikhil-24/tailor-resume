import json
import os
import random
import time
from google import genai
from google.genai import errors, types
from dotenv import load_dotenv

from .prompts import (
    build_suggestions_prompt,
    build_cover_letter_prompt,
    SUGGESTIONS_SYSTEM_PROMPT,
    COVER_LETTER_SYSTEM_PROMPT,
)
from .cover_letter import save_cover_letter

load_dotenv()

_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

_MAX_ATTEMPTS = 5
_RETRY_BASE_DELAY_SECONDS = 2
_RETRY_MAX_DELAY_SECONDS = 30


def _response_text(response) -> str:
    # response.text raises if the response was blocked / has no candidates.
    try:
        return (response.text or "").strip()
    except Exception:
        return ""


def _generate_with_retry(prompt: str, system_instruction: str, json_mode: bool):
    config_kwargs = {"system_instruction": system_instruction}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    # Retries on server errors AND empty responses (both are "total failures" in practice).
    # ponytail: catches errors.ServerError; if client-side timeouts surface as another type, widen here.
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            response = _client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )
            if _response_text(response):
                return response
        except errors.ServerError:
            if attempt == _MAX_ATTEMPTS:
                raise
        if attempt < _MAX_ATTEMPTS:
            # Exponential backoff with jitter — rides out sustained 503 overloads, not just blips.
            delay = min(_RETRY_BASE_DELAY_SECONDS * 2 ** (attempt - 1), _RETRY_MAX_DELAY_SECONDS)
            time.sleep(delay + random.uniform(0, 1))
    return response  # exhausted retries on empty responses; let the caller surface the failure


def _parse_json(text: str) -> dict:
    start = text.find("{")
    depth = 0
    end = start
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return json.loads(text[start:end])


def _is_complete(resume_data: dict, suggestions: dict) -> bool:
    """True if the response covers every bullet, project, and skill category the resume has."""
    expected_bullets = {
        b["paragraph_index"] for role in resume_data.get("experience", []) for b in role["bullets"]
    }
    got_bullets = {
        b.get("paragraph_index")
        for role in suggestions.get("experience", [])
        for b in role.get("bullets", [])
    }
    if not expected_bullets <= got_bullets:
        return False

    expected_projects = {p["title_paragraph_index"] for p in resume_data.get("projects", [])}
    got_projects = {p.get("title_paragraph_index") for p in suggestions.get("projects", [])}
    if not expected_projects <= got_projects:
        return False

    expected_cats = len(resume_data.get("skills", []))
    got_cats = len(suggestions.get("skills", {}).get("reordered_categories", []))
    return got_cats >= expected_cats


def get_suggestions(resume_data: dict, jd: str, tone: str = "Concise & Technical") -> dict:
    prompt = build_suggestions_prompt(resume_data, jd, tone)

    # One extra shot if the model drops bullets/projects/skill categories.
    suggestions = None
    for _ in range(2):
        response = _generate_with_retry(prompt, SUGGESTIONS_SYSTEM_PROMPT, json_mode=True)
        suggestions = _parse_json(_response_text(response))
        if _is_complete(resume_data, suggestions):
            return suggestions
    return suggestions  # best effort after retry


def generate_cover_letter(
    company: str,
    job_title: str,
    jd: str,
    accepted_summary: str,
    accepted_bullets: list[str],
) -> str:
    prompt = build_cover_letter_prompt(company, job_title, jd, accepted_summary, accepted_bullets)
    response = _generate_with_retry(prompt, COVER_LETTER_SYSTEM_PROMPT, json_mode=False)

    return save_cover_letter(response.text, company, job_title)
