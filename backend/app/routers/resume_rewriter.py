from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeRewriteRequest, ResumeRewriteResponse
from app.services.resume_service import resume_service

router = APIRouter(prefix="/resume", tags=["Resume Rewriter"])


@router.post("/rewrite", response_model=ResumeRewriteResponse)
async def rewrite_bullet(
    data: ResumeRewriteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        result = await resume_service.rewrite_bullet(data.bullet_point, data.context)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return ResumeRewriteResponse(
        original=data.bullet_point,
        rewritten=result.get("rewritten", ""),
        improvements=result.get("improvements", []),
    )