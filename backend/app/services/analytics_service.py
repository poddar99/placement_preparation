from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dsa import DSAProgress, DSATopic
from app.services.llm_service import llm_service
from app.services.placement_metrics_service import compute_placement_metrics


class AnalyticsService:
    """Compute placement readiness analytics from DB + optional LLM insights."""

    async def compute_analytics(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        metrics = await compute_placement_metrics(db, user_id)

        topics_result = await db.execute(select(DSATopic))
        topics = list(topics_result.scalars().all())

        progress_result = await db.execute(
            select(DSAProgress).where(DSAProgress.user_id == user_id)
        )
        progress_map = {p.topic_id: p for p in progress_result.scalars().all()}

        topic_breakdown: List[Dict[str, Any]] = []
        strong_areas: List[str] = []
        weak_areas: List[str] = []

        for topic in topics:
            prog = progress_map.get(topic.id)
            solved = prog.problems_solved if prog else 0
            raw_pct = (solved / topic.total_problems * 100) if topic.total_problems > 0 else 0
            pct = min(100.0, round(raw_pct, 1))

            topic_breakdown.append({
                "topic_name": topic.name,
                "progress_percent": pct,
                "problems_solved": solved,
                "total_problems": topic.total_problems,
            })

            if pct >= 70:
                strong_areas.append(topic.name)
            elif pct < 30:
                weak_areas.append(topic.name)

        llm_insights = await self._generate_insights(
            dsa_completion=metrics.dsa_progress_percent,
            strong_areas=strong_areas,
            weak_areas=weak_areas,
            readiness_score=metrics.readiness_score,
            resume_score=metrics.resume_score,
            mock_percent=metrics.mock_interview_score,
        )

        return {
            "dsa_completion_percent": metrics.dsa_progress_percent,
            "strong_areas": strong_areas,
            "weak_areas": weak_areas,
            "readiness_score": metrics.readiness_score,
            "topic_breakdown": topic_breakdown,
            "cs_subjects": [],
            "resume_score": metrics.resume_score,
            "mock_interview_avg": metrics.mock_interview_score,
            "llm_insights": llm_insights,
        }

    async def _generate_insights(
        self,
        dsa_completion: float,
        strong_areas: List[str],
        weak_areas: List[str],
        readiness_score: int,
        resume_score: Optional[float],
        mock_percent: Optional[float],
    ) -> str:
        prompt = f"""Based on this placement preparation data, give 3-4 concise actionable insights (bullet points):

- DSA completion: {dsa_completion:.0f}%
- Strong areas: {strong_areas or 'None yet'}
- Weak areas: {weak_areas or 'None identified'}
- Readiness score: {readiness_score}/100
- Resume score: {f'{resume_score:.0f}%' if resume_score is not None else 'Not analyzed'}
- Mock interview score: {f'{mock_percent:.0f}%' if mock_percent is not None else 'Not attempted'}

Be specific and encouraging. No JSON, just plain text bullet points."""

        try:
            return await llm_service.generate(prompt, temperature=0.6)
        except RuntimeError:
            return "Continue practicing DSA daily and attempt mock interviews to improve readiness."


analytics_service = AnalyticsService()