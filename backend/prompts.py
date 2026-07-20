import json

SUGGESTIONS_SYSTEM_PROMPT = "You are a resume tailoring assistant. Return only valid JSON. No prose, no markdown, no code fences."
COVER_LETTER_SYSTEM_PROMPT = "You are a professional cover letter writer. Write concise, honest cover letters using only the provided information."

_TONE_INSTRUCTIONS = {
    "Results-Driven": "Write the summary to emphasise measurable impact and quantifiable outcomes.",
    "Research-Oriented": "Write the summary to highlight academic rigour, publications, and research contributions.",
    "Startup-Focused": "Write the summary to convey ownership, scrappiness, and ability to operate in ambiguous fast-moving environments.",
}

# Applies on every tone (including the default, which has no _TONE_INSTRUCTIONS entry).
_SUMMARY_GUIDANCE = (
    "Rewrite the professional summary so it reads like a strong, specific candidate for THIS role. "
    "Open with the candidate's title/level, then name 2-3 of the most JD-relevant strengths drawn from the resume. "
    "Be concrete. Ban filler adjectives ('passionate', 'hard-working', 'results-oriented', 'detail-oriented'). "
    "Keep it to 2-3 sentences."
)

# Few-shot: show the model the transformation, don't just describe it. SWE-domain.
# Strong versions strengthen the verb and add specificity WITHOUT inventing metrics.
_BULLET_EXAMPLES = """Examples of the rewriting quality expected (weak -> strong):
- Weak: "Responsible for the backend and fixing bugs."
  Strong: "Engineered and maintained the Node.js REST backend, resolving high-priority production bugs that unblocked the checkout flow."
- Weak: "Worked on a machine learning project for predicting customer churn."
  Strong: "Built a customer-churn prediction model in Python/scikit-learn and integrated it into the retention dashboard used by the support team."
"""


def build_suggestions_prompt(resume_data: dict, jd: str, tone: str = "Concise & Technical") -> str:
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

    tone_instruction = _TONE_INSTRUCTIONS.get(tone, "")
    summary_line = f"- {_SUMMARY_GUIDANCE}" + (f" {tone_instruction}" if tone_instruction else "")

    return f"""Professional summary:
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
- Do not invent or copy claims (years of experience, credentials, metrics) that are not already present in the resume content above, even if the job description states them as requirements.
{summary_line}
- Rewrite each experience bullet to target the job description. Lead with a strong past-tense action verb (Built, Led, Shipped, Automated, Reduced, Designed). Mirror the JD's terminology wherever the resume truthfully supports it. Never use filler openers ('Responsible for', 'Worked on', 'Helped with', 'Leveraged', 'Utilized'). Keep any metric already in the original bullet; do not invent new numbers. Keep each bullet to a single line.
- Reorder skill categories by relevance to the JD (most relevant first). Reorder items within each category by relevance. Return ALL {len(resume_data.get('skills', []))} categories.
- Suggest skills from the JD that are missing from the resume (suggested_additions may be empty if none).
- Rank ALL {len(resume_data.get('projects', []))} projects by relevance to the JD (relevance_score 0-100, ordered highest first).
- For each optional section, recommend keep or drop based on JD relevance and one-page constraint.
- List any JD-required skills or keywords completely absent from the resume in gaps (may be empty).

{_BULLET_EXAMPLES}
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


def build_cover_letter_prompt(
    company: str,
    job_title: str,
    jd: str,
    accepted_summary: str,
    accepted_bullets: list[str],
) -> str:
    bullets_text = "\n".join(f"- {b}" for b in accepted_bullets) if accepted_bullets else "(none provided)"

    return f"""Write a professional cover letter for the following position.

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
