from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.interview import InterviewAskRequest, InterviewAskResponse, InterviewIngestRequest, InterviewIngestResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix="/interview", tags=["Interview Experience RAG"])


@router.post("/ask", response_model=InterviewAskResponse)
async def ask_interview_question(
    data: InterviewAskRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        sources, answer = await rag_service.query(
            question=data.question,
            company=data.company,
            role=data.role,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return InterviewAskResponse(answer=answer, sources=sources)


@router.post("/ingest", response_model=InterviewIngestResponse)
async def ingest_interview_experience(
    data: InterviewIngestRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        doc_id = await rag_service.ingest_experience(
            company=data.company,
            role=data.role,
            experience=data.experience,
            outcome=data.outcome,
            difficulty=data.difficulty,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest experience: {e}")

    return InterviewIngestResponse(id=doc_id, message="Interview experience ingested successfully")