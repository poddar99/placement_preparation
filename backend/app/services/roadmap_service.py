from typing import Any, Dict, List, Optional

from app.services.llm_service import llm_service


class RoadmapService:
    """LLM-generated company-specific preparation roadmaps."""

    async def generate_roadmap(
        self,
        company_name: str,
        company_description: str,
        hiring_process: Optional[str],
        user_context: Dict[str, Any],
        weeks_available: int = 12,
        focus_areas: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        system = (
            "You are a placement preparation mentor creating personalized study roadmaps "
            "for software engineering students targeting specific companies."
        )

        dsa_progress = user_context.get("dsa_progress", [])
        weak_areas = user_context.get("weak_areas", [])
        strong_areas = user_context.get("strong_areas", [])

        prompt = f"""Create a personalized preparation roadmap for targeting {company_name}.

Company info:
- Description: {company_description}
- Hiring process: {hiring_process or 'Standard online test + technical interviews + HR round'}

Student profile:
- College: {user_context.get('college', 'N/A')}
- Branch: {user_context.get('branch', 'N/A')}
- Graduation year: {user_context.get('graduation_year', 'N/A')}
- DSA progress: {dsa_progress}
- Strong areas: {strong_areas}
- Weak areas: {weak_areas}
- Weeks available: {weeks_available}
- Focus areas: {focus_areas or 'All areas'}

Return JSON with:
- overview: string (brief roadmap summary)
- timeline_weeks: number
- phases: list of objects, each with:
  - week_range: string (e.g. "Week 1-2")
  - title: string
  - topics: list of strings
  - resources: list of strings (books, websites, practice platforms)
  - milestones: list of strings
- dsa_focus: list of strings (priority DSA topics for this company)
- cs_subjects: list of strings (OS, DBMS, CN, etc. to focus on)
- mock_interview_tips: list of strings
- daily_schedule: string (suggested daily study routine)
"""

        result = await llm_service.generate_json(prompt, system=system, temperature=0.6)

        if result.get("parse_error"):
            result = {
                "overview": f"Preparation roadmap for {company_name}",
                "timeline_weeks": weeks_available,
                "phases": [],
                "dsa_focus": weak_areas or ["Arrays", "Trees", "Dynamic Programming"],
                "cs_subjects": ["OS", "DBMS", "Computer Networks"],
                "mock_interview_tips": ["Practice coding on LeetCode", "Review CS fundamentals"],
                "daily_schedule": "2 hours DSA + 1 hour CS subjects + 30 min mock interview",
                "raw_response": result.get("raw_response"),
            }

        return result


roadmap_service = RoadmapService()