import os
from datetime import date
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = anthropic.Anthropic()
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def generate_cover_letter(
    company: str,
    job_title: str,
    jd: str,
    accepted_summary: str,
    accepted_bullets: list[str],
) -> str:
    bullets_text = "\n".join(f"- {b}" for b in accepted_bullets) if accepted_bullets else "(none provided)"

    prompt = f"""Write a professional cover letter for the following position.

Company: {company}
Job title: {job_title}

Job description:
{jd}

Candidate's professional summary:
{accepted_summary}

Candidate's key experience highlights:
{bullets_text}

Requirements:
- Three paragraphs
- Professional tone
- Reference only the information provided above — do not invent facts, credentials, or experience not mentioned
- No salutation header or signature block — plain body paragraphs only
- Plain text, no markdown or bullet points"""

    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        system="You are a professional cover letter writer. Write concise, honest cover letters using only the provided information.",
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    today = date.today().strftime("%Y-%m-%d")
    safe_company = company.strip().replace(" ", "_")
    safe_title = job_title.strip().replace(" ", "_")
    filename = f"CoverLetter_{safe_company}_{safe_title}_{today}.txt"
    output_path = os.path.join(_PROJECT_ROOT, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return output_path
