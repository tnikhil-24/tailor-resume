import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = anthropic.Anthropic()


def get_summary_suggestion(summary_text: str, jd: str) -> dict:
    prompt = f"""Professional summary from resume:
{summary_text}

Job description:
{jd}

Return only this JSON, no other text:
{{"summary": {{"suggested": "<rewritten summary targeting this specific job>"}}}}"""

    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are a resume tailoring assistant. Return only valid JSON. No prose, no markdown, no code fences.",
        messages=[{"role": "user", "content": prompt}],
    )

    return json.loads(response.content[0].text)
