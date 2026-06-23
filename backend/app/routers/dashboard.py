from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.placement_metrics_service import compute_placement_metrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    metrics = await compute_placement_metrics(db, current_user.id)

    return DashboardResponse(
        dsa_progress_percent=metrics.dsa_progress_percent,
        cs_subjects_progress=[],
        resume_score=metrics.resume_score,
        mock_interview_score=metrics.mock_interview_score,
        contest_rating=metrics.contest_rating,
        current_streak=0,
        total_problems_solved=metrics.total_problems_solved,
        readiness_score=metrics.readiness_score,
        upcoming_companies=[],
    )