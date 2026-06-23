from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.company import Company
from app.models.dsa import DSAProgress, DSATopic, UserStats
from app.models.interview import CSSubjectProgress, MockInterviewSession
from app.models.resume import ResumeReport
from app.models.user import User
from app.schemas.dashboard import CSSubjectProgressItem, DashboardResponse, UpcomingCompany

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    topics_result = await db.execute(select(DSATopic))
    topics = list(topics_result.scalars().all())

    progress_result = await db.execute(
        select(DSAProgress).where(DSAProgress.user_id == current_user.id)
    )
    progress_map = {p.topic_id: p for p in progress_result.scalars().all()}

    total_solved = 0
    total_problems = 0
    for topic in topics:
        prog = progress_map.get(topic.id)
        total_solved += prog.problems_solved if prog else 0
        total_problems += topic.total_problems

    dsa_percent = (total_solved / total_problems * 100) if total_problems > 0 else 0

    cs_result = await db.execute(
        select(CSSubjectProgress).where(CSSubjectProgress.user_id == current_user.id)
    )
    cs_subjects = [
        CSSubjectProgressItem(subject_name=s.subject_name, progress_percent=s.progress_percent)
        for s in cs_result.scalars().all()
    ]

    resume_result = await db.execute(
        select(ResumeReport)
        .where(ResumeReport.user_id == current_user.id)
        .order_by(ResumeReport.created_at.desc())
        .limit(1)
    )
    latest_resume = resume_result.scalar_one_or_none()

    mock_result = await db.execute(
        select(MockInterviewSession.overall_score)
        .where(
            MockInterviewSession.user_id == current_user.id,
            MockInterviewSession.overall_score.isnot(None),
        )
        .order_by(MockInterviewSession.created_at.desc())
        .limit(1)
    )
    latest_mock_score = mock_result.scalar_one_or_none()

    stats_result = await db.execute(
        select(UserStats).where(UserStats.user_id == current_user.id)
    )
    stats = stats_result.scalar_one_or_none()

    upcoming: List[UpcomingCompany] = []
    if current_user.target_companies:
        companies_result = await db.execute(
            select(Company).where(Company.name.in_(current_user.target_companies))
        )
        for company in companies_result.scalars().all():
            upcoming.append(UpcomingCompany(
                id=company.id,
                name=company.name,
                difficulty_level=company.difficulty_level,
                description=company.description,
            ))
    else:
        companies_result = await db.execute(select(Company).limit(5))
        for company in companies_result.scalars().all():
            upcoming.append(UpcomingCompany(
                id=company.id,
                name=company.name,
                difficulty_level=company.difficulty_level,
                description=company.description,
            ))

    cs_avg = (
        sum(s.progress_percent for s in cs_subjects) / len(cs_subjects)
        if cs_subjects
        else 0.0
    )
    resume_component = latest_resume.score if latest_resume and latest_resume.score else 0.0
    mock_component = latest_mock_score if latest_mock_score else 0.0
    readiness = round(
        (dsa_percent * 0.4) + (cs_avg * 0.2) + (resume_component * 0.2) + (mock_component * 0.2),
        1,
    )

    return DashboardResponse(
        dsa_progress_percent=round(dsa_percent, 1),
        cs_subjects_progress=cs_subjects,
        resume_score=latest_resume.score if latest_resume else None,
        mock_interview_score=latest_mock_score,
        contest_rating=stats.contest_rating if stats else 0,
        current_streak=stats.current_streak if stats else 0,
        total_problems_solved=stats.total_problems_solved if stats else 0,
        readiness_score=readiness,
        upcoming_companies=upcoming,
    )