from typing import Any, Dict

from app.services.llm_service import llm_service


class ResumeService:
    """Resume analysis and rewriting via LLM."""

    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        system = (
            "You are an expert technical recruiter and resume coach for software engineering placements. "
            "Analyze resumes critically and provide actionable feedback."
        )

        prompt = f"""Analyze the following resume text and return a JSON object with these exact keys:
- strengths: list of strings (3-5 key strengths)
- weaknesses: list of strings (3-5 areas to improve)
- missing_skills: list of strings (skills commonly expected but missing)
- suggested_projects: list of strings (2-4 project ideas to strengthen the resume)
- score: number from 0 to 100 (overall resume quality score)
- summary: string (2-3 sentence overall assessment)

Resume text:
{resume_text[:8000]}
"""

        result = await llm_service.generate_json(prompt, system=system, temperature=0.4)

        if result.get("parse_error"):
            result = {
                "strengths": ["Resume uploaded successfully"],
                "weaknesses": ["Could not fully parse LLM response"],
                "missing_skills": [],
                "suggested_projects": [],
                "score": 50.0,
                "summary": result.get("raw_response", "Analysis pending"),
            }

        score = float(result.get("score", 50))
        result["score"] = max(0, min(100, score))
        return result

    async def rewrite_bullet(self, bullet_point: str, context: str | None = None) -> Dict[str, Any]:
        system = (
            "You are a professional resume writer specializing in tech roles. "
            "Rewrite bullet points using strong action verbs, quantifiable metrics, and ATS-friendly language."
        )

        prompt = f"""Rewrite this resume bullet point professionally.

Original bullet: {bullet_point}
{f'Additional context: {context}' if context else ''}

Return JSON with:
- rewritten: string (the improved bullet point)
- improvements: list of strings (what was improved)
"""

        result = await llm_service.generate_json(prompt, system=system, temperature=0.6)

        if result.get("parse_error"):
            rewritten = await llm_service.generate(
                f"Rewrite this resume bullet professionally: {bullet_point}",
                system=system,
            )
            result = {
                "rewritten": rewritten,
                "improvements": ["Used action verbs", "Added impact focus"],
            }

        return result


resume_service = ResumeService()