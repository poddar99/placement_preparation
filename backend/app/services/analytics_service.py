from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dsa import DSAProgress, DSATopic, UserStats
from app.models.interview import CSSubjectProgress, MockInterviewSession
from app.models.resume import ResumeReport
from app.services.llm_service import llm_service


class AnalyticsService:
    """Compute placement readiness analytics from DB + optional LLM insights."""

    async def compute_analytics(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        topics_result = await db.execute(select(DSATopic))
        topics = list(topics_result.scalars().all())

        progress_result = await db.execute(
            select(DSAProgress).where(DSAProgress.user_id == user_id)
        )
        progress_map = {p.topic_id: p for p in progress_result.scalars().all()}

        topic_breakdown: List[Dict[str, Any]] = []
        strong_areas: List[str] = []
        weak_areas: List[str] = []
        total_solved = 0
        total_problems = 0

        for topic in topics:
            prog = progress_map.get(topic.id)
            solved = prog.problems_solved if prog else 0
            total_solved += solved
            total_problems += topic.total_problems
            pct = (solved / topic.total_problems * 100) if topic.total_problems > 0 else 0

            topic_breakdown.append({
                "topic_name": topic.name,
                "progress_percent": round(pct, 1),
                "problems_solved": solved,
                "total_problems": topic.total_problems,
            })

            if pct >= 70:
                strong_areas.append(topic.name)
            elif pct < 30:
                weak_areas.append(topic.name)

        dsa_completion = (total_solved / total_problems * 100) if total_problems > 0 else 0

        cs_result = await db.execute(
            select(CSSubjectProgress).where(CSSubjectProgress.user_id == user_id)
        )
        cs_subjects = [
            {"subject_name": s.subject_name, "progress_percent": s.progress_percent}
            for s in cs_result.scalars().all()
        ]

        resume_result = await db.execute(
            select(ResumeReport)
            .where(ResumeReport.user_id == user_id)
            .order_by(ResumeReport.created_at.desc())
            .limit(1)
        )
        latest_resume = resume_result.scalar_one_or_none()
        resume_score = latest_resume.score if latest_resume else None

        mock_result = await db.execute(
            select(func.avg(MockInterviewSession.overall_score))
            .where(
                MockInterviewSession.user_id == user_id,
                MockInterviewSession.overall_score.isnot(None),
            )
        )
        mock_avg = mock_result.scalar()

        stats_result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats = stats_result.scalar_one_or_none()

        readiness = self._compute_readiness(
            dsa_completion=dsa_completion,
            resume_score=resume_score,
            mock_avg=mock_avg,
            contest_rating=stats.contest_rating if stats else 0,
            cs_subjects=cs_subjects,
        )

        llm_insights = await self._generate_insights(
            dsa_completion=dsa_completion,
            strong_areas=strong_areas,
            weak_areas=weak_areas,
            readiness_score=readiness,
            resume_score=resume_score,
            mock_avg=mock_avg,
        )

        return {
            "dsa_completion_percent": round(dsa_completion, 1),
            "strong_areas": strong_areas,
            "weak_areas": weak_areas,
            "readiness_score": round(readiness, 1),
            "topic_breakdown": topic_breakdown,
            "cs_subjects": cs_subjects,
            "resume_score": resume_score,
            "mock_interview_avg": round(mock_avg, 1) if mock_avg else None,
            "llm_insights": llm_insights,
        }

    def _compute_readiness(
        self,
        dsa_completion: float,
        resume_score: Optional[float],
        mock_avg: Optional[float],
        contest_rating: int,
        cs_subjects: List[Dict[str, Any]],
    ) -> float:
        weights = {"dsa": 0.35, "resume": 0.2, "mock": 0.25, "cs": 0.1, "contest": 0.1}

        dsa_score = dsa_completion
        resume_component = resume_score if resume_score is not None else 50
        mock_component = (mock_avg / 10 * 100) if mock_avg is not None else 50
        cs_avg = (
            sum(s["progress_percent"] for s in cs_subjects) / len(cs_subjects)
            if cs_subjects
            else 50
        )
        contest_component = min(contest_rating / 20, 100) if contest_rating > 0 else 30

        readiness = (
            dsa_score * weights["dsa"]
            + resume_component * weights["resume"]
            + mock_component * weights["mock"]
            + cs_avg * weights["cs"]
            + contest_component * weights["contest"]
        )
        return min(100, max(0, readiness))

    async def _generate_insights(
        self,
        dsa_completion: float,
        strong_areas: List[str],
        weak_areas: List[str],
        readiness_score: float,
        resume_score: Optional[float],
        mock_avg: Optional[float],
    ) -> str:
        prompt = f"""Based on this placement preparation data, give 3-4 concise actionable insights (bullet points):

- DSA completion: {dsa_completion:.1f}%
- Strong areas: {strong_areas or 'None yet'}
- Weak areas: {weak_areas or 'None identified'}
- Readiness score: {readiness_score:.1f}/100
- Resume score: {resume_score or 'Not analyzed'}
- Mock interview avg: {mock_avg or 'Not attempted'}/10

Be specific and encouraging. No JSON, just plain text bullet points."""

        try:
            return await llm_service.generate(prompt, temperature=0.6)
        except RuntimeError:
            return "Continue practicing DSA daily and attempt mock interviews to improve readiness."


analytics_service = AnalyticsService()