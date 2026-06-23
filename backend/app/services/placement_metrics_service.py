from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dsa import DSAProgress, DSATopic, UserStats
from app.models.interview import MockInterviewSession
from app.models.resume import ResumeReport


@dataclass
class PlacementMetrics:
    dsa_progress_percent: float
    resume_score: Optional[float]
    mock_interview_score: float
    readiness_score: int
    total_problems_solved: int
    contest_rating: int


def mock_score_percent(session: MockInterviewSession) -> Optional[float]:
    """Convert mock interview score (0–10 scale) to a 0–100 percentage."""
    if session.overall_score is not None:
        return min(100.0, round(session.overall_score * 10, 1))

    evaluations = (session.scores_json or {}).get("evaluations", [])
    if not evaluations:
        return None

    avg = sum(e.get("score", 0) for e in evaluations) / len(evaluations)
    return min(100.0, round(avg * 10, 1))


def compute_readiness(
    dsa_percent: float,
    resume_score: Optional[float],
    mock_percent: Optional[float],
) -> int:
    resume_component = resume_score if resume_score is not None else 0.0
    mock_component = mock_percent if mock_percent is not None else 0.0
    return round((dsa_percent * 0.5) + (resume_component * 0.25) + (mock_component * 0.25))


async def compute_placement_metrics(db: AsyncSession, user_id: int) -> PlacementMetrics:
    topics_result = await db.execute(select(DSATopic))
    topics = list(topics_result.scalars().all())

    progress_result = await db.execute(
        select(DSAProgress).where(DSAProgress.user_id == user_id)
    )
    progress_map = {p.topic_id: p for p in progress_result.scalars().all()}

    total_problems = sum(topic.total_problems for topic in topics)

    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
    stats = stats_result.scalar_one_or_none()

    if stats and stats.total_problems_solved:
        total_solved = stats.total_problems_solved
    else:
        total_solved = sum(
            (progress_map.get(topic.id).problems_solved if progress_map.get(topic.id) else 0)
            for topic in topics
        )

    raw_dsa_percent = (total_solved / total_problems * 100) if total_problems > 0 else 0
    dsa_percent = min(100.0, round(raw_dsa_percent, 1))

    resume_result = await db.execute(
        select(ResumeReport)
        .where(ResumeReport.user_id == user_id)
        .order_by(ResumeReport.created_at.desc())
        .limit(1)
    )
    latest_resume = resume_result.scalar_one_or_none()
    resume_score = latest_resume.score if latest_resume else None

    mock_result = await db.execute(
        select(MockInterviewSession)
        .where(MockInterviewSession.user_id == user_id)
        .order_by(MockInterviewSession.created_at.desc())
    )
    latest_mock_percent: Optional[float] = None
    for session in mock_result.scalars().all():
        percent = mock_score_percent(session)
        if percent is not None:
            latest_mock_percent = percent
            break

    return PlacementMetrics(
        dsa_progress_percent=dsa_percent,
        resume_score=resume_score,
        mock_interview_score=latest_mock_percent or 0.0,
        readiness_score=compute_readiness(dsa_percent, resume_score, latest_mock_percent),
        total_problems_solved=stats.total_problems_solved if stats else total_solved,
        contest_rating=stats.contest_rating if stats else 0,
    )