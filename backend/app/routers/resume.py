import os
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.resume import ResumeReport
from app.models.user import User
from app.schemas.resume import ResumeReportResponse
from app.services.resume_service import resume_service
from app.utils.pdf import extract_pdf_text

router = APIRouter(prefix="/resume", tags=["Resume Analyzer"])
settings = get_settings()


@router.post("/analyze", response_model=ResumeReportResponse)
async def analyze_resume(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.max_upload_size_mb}MB")

    text = extract_pdf_text(content)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    try:
        analysis = await resume_service.analyze_resume(text)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    os.makedirs(settings.upload_dir, exist_ok=True)

    report = ResumeReport(
        user_id=current_user.id,
        filename=file.filename,
        raw_text=text,
        analysis_json=analysis,
        score=float(analysis.get("score", 0)),
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    return ResumeReportResponse.model_validate(report)


@router.get("/reports", response_model=List[ResumeReportResponse])
async def list_reports(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(ResumeReport)
        .where(ResumeReport.user_id == current_user.id)
        .order_by(ResumeReport.created_at.desc())
    )
    return [ResumeReportResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/reports/{report_id}", response_model=ResumeReportResponse)
async def get_report(
    report_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(ResumeReport).where(
            ResumeReport.id == report_id,
            ResumeReport.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ResumeReportResponse.model_validate(report)