import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = anthropic.Anthropic()


def get_suggestions(resume_data: dict, jd: str) -> dict:
    experience_text = ""
    for role in resume_data.get("experience", []):
        experience_text += f"\n[{role['company']}]\n"
        for b in role["bullets"]:
            experience_text += f"  (idx:{b['paragraph_index']}) {b['text']}\n"

    experience_json = json.dumps([
        {
            "company": role["company"],
            "bullets": [
                {"paragraph_index": b["paragraph_index"], "suggested": "<rewrite>", "reason": "<reason>"}
                for b in role["bullets"]
            ],
        }
        for role in resume_data.get("experience", [])
    ], indent=2)

    prompt = f"""Professional summary:
{resume_data['summary']['text']}

Work experience bullets:
{experience_text}
Job description:
{jd}

Return only this JSON structure, no other text. For each bullet, rewrite it to better match the job description:
{{
  "summary": {{"suggested": "<rewritten summary>"}},
  "experience": {experience_json}
}}"""

    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="You are a resume tailoring assistant. Return only valid JSON. No prose, no markdown, no code fences.",
        messages=[{"role": "user", "content": prompt}],
    )

    return json.loads(response.content[0].text)
