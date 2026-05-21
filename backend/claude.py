import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = anthropic.Anthropic()


def get_suggestions(resume_data: dict, jd: str) -> dict:
    # Build experience text
    experience_text = ""
    for role in resume_data.get("experience", []):
        experience_text += f"\n[{role['company']}]\n"
        for b in role["bullets"]:
            experience_text += f"  (idx:{b['paragraph_index']}) {b['text']}\n"

    # Build skills text
    skills_text = ""
    for s in resume_data.get("skills", []):
        skills_text += f"  (idx:{s['paragraph_index']}) {s['category']}: {', '.join(s['items'])}\n"

    # Build projects text (titles + tech only — no bullets to stay within token budget)
    projects_text = ""
    for p in resume_data.get("projects", []):
        projects_text += f"  (idx:{p['title_paragraph_index']}) {p['title']} | {p['tech']}\n"

    # Build optional sections text
    opt = resume_data.get("optional_sections", {})
    optional_text = ""
    for key, label in [("research_paper", "Research Paper"), ("achievements", "Achievements"), ("certifications", "Certifications")]:
        section = opt.get(key, {})
        if section:
            optional_text += f"[{label}]\n"
            for t in section.get("texts", []):
                optional_text += f"  {t}\n"

    # Build JSON templates for response
    experience_template = json.dumps([
        {
            "company": role["company"],
            "bullets": [
                {"paragraph_index": b["paragraph_index"], "suggested": "<rewrite>", "reason": "<reason>"}
                for b in role["bullets"]
            ],
        }
        for role in resume_data.get("experience", [])
    ], indent=2)

    skills_template = json.dumps({
        "reordered_categories": [
            {"paragraph_index": s["paragraph_index"], "category": s["category"], "items": s["items"]}
            for s in resume_data.get("skills", [])
        ],
        "suggested_additions": [
            {"category": "<category from above>", "skill": "<skill from JD not in resume>", "reason": "<why>"}
        ],
    }, indent=2)

    projects_template = json.dumps([
        {"title": p["title"], "title_paragraph_index": p["title_paragraph_index"], "relevance_score": 0, "reason": "<why>"}
        for p in resume_data.get("projects", [])
    ], indent=2)

    prompt = f"""Professional summary:
{resume_data['summary']['text']}

Work experience:
{experience_text}

Skills:
{skills_text}

Projects (title | tech stack):
{projects_text}

Optional sections:
{optional_text}

Job description:
{jd}

Return only this JSON, no other text.
- Rewrite the summary to target this specific job.
- Rewrite each experience bullet to better match the job description keywords and tone.
- Reorder skill categories by relevance to the JD (most relevant first). Reorder items within each category by relevance. Return ALL {len(resume_data.get('skills', []))} categories.
- Suggest skills from the JD that are missing from the resume (suggested_additions may be empty if none).
- Rank ALL {len(resume_data.get('projects', []))} projects by relevance to the JD (relevance_score 0-100, ordered highest first).
- For each optional section, recommend keep or drop based on JD relevance and one-page constraint.
- List any JD-required skills or keywords completely absent from the resume in gaps (may be empty).

{{
  "summary": {{"suggested": "<rewritten summary>"}},
  "experience": {experience_template},
  "skills": {skills_template},
  "projects": {projects_template},
  "optional_sections": {{
    "research_paper": {{"keep": true, "reason": "<why>"}},
    "achievements": {{"keep": true, "reason": "<why>"}},
    "certifications": {{"keep": true, "reason": "<why>"}}
  }},
  "gaps": ["<skill or keyword from JD not in resume>"]
}}"""

    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system="You are a resume tailoring assistant. Return only valid JSON. No prose, no markdown, no code fences.",
        messages=[{"role": "user", "content": prompt}],
    )

    return json.loads(response.content[0].text)
