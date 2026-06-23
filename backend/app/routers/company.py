from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.company import Company, Roadmap
from app.models.dsa import DSAProgress, DSATopic
from app.models.user import User
from app.schemas.company import CompanyResponse, RoadmapGenerateRequest, RoadmapResponse
from app.services.roadmap_service import roadmap_service

router = APIRouter(prefix="/companies", tags=["Company Roadmaps"])


@router.get("", response_model=List[CompanyResponse])
async def list_companies(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Company).order_by(Company.name))
    return [CompanyResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/{company_id}/roadmap", response_model=RoadmapResponse)
async def generate_roadmap(
    company_id: int,
    data: RoadmapGenerateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    company_result = await db.execute(select(Company).where(Company.id == company_id))
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    progress_result = await db.execute(
        select(DSAProgress, DSATopic)
        .join(DSATopic, DSAProgress.topic_id == DSATopic.id)
        .where(DSAProgress.user_id == current_user.id)
    )
    progress_rows = progress_result.all()

    dsa_progress = []
    weak_areas = []
    strong_areas = []
    for prog, topic in progress_rows:
        pct = (prog.problems_solved / topic.total_problems * 100) if topic.total_problems > 0 else 0
        dsa_progress.append(f"{topic.name}: {prog.problems_solved}/{topic.total_problems}")
        if pct >= 70:
            strong_areas.append(topic.name)
        elif pct < 30:
            weak_areas.append(topic.name)

    user_context = {
        "college": current_user.college,
        "branch": current_user.branch,
        "graduation_year": current_user.graduation_year,
        "dsa_progress": dsa_progress,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas,
    }

    try:
        content = await roadmap_service.generate_roadmap(
            company_name=company.name,
            company_description=company.description or "",
            hiring_process=company.hiring_process,
            user_context=user_context,
            weeks_available=data.weeks_available or 12,
            focus_areas=data.focus_areas,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    roadmap = Roadmap(
        user_id=current_user.id,
        company_id=company.id,
        content_json=content,
    )
    db.add(roadmap)
    await db.flush()
    await db.refresh(roadmap)

    return RoadmapResponse(
        id=roadmap.id,
        company_id=company.id,
        company_name=company.name,
        content_json=roadmap.content_json,
        created_at=roadmap.created_at,
    )


@router.get("/roadmaps", response_model=List[RoadmapResponse])
async def list_roadmaps(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Roadmap, Company)
        .join(Company, Roadmap.company_id == Company.id)
        .where(Roadmap.user_id == current_user.id)
        .order_by(Roadmap.created_at.desc())
    )
    responses = []
    for roadmap, company in result.all():
        responses.append(RoadmapResponse(
            id=roadmap.id,
            company_id=company.id,
            company_name=company.name,
            content_json=roadmap.content_json,
            created_at=roadmap.created_at,
        ))
    return responses