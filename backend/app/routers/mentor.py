from collections import defaultdict
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.mentor import ChatMessageResponse, MentorChatRequest, MentorChatResponse, MentorHistoryResponse
from app.services.mentor_service import mentor_service

router = APIRouter(prefix="/mentor", tags=["AI Mentor"])


@router.post("/chat", response_model=MentorChatResponse)
async def mentor_chat(
    data: MentorChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_profile = {
        "full_name": current_user.full_name,
        "college": current_user.college,
        "branch": current_user.branch,
        "graduation_year": current_user.graduation_year,
        "target_companies": current_user.target_companies,
    }

    try:
        session_id, reply = await mentor_service.chat(
            db=db,
            user_id=current_user.id,
            message=data.message,
            session_id=data.session_id,
            user_profile=user_profile,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return MentorChatResponse(session_id=session_id, reply=reply)


@router.get("/history", response_model=List[MentorHistoryResponse])
async def mentor_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    session_id: Optional[str] = Query(None),
):
    messages = await mentor_service.get_history(db, current_user.id, session_id)

    if session_id:
        return [MentorHistoryResponse(
            session_id=session_id,
            messages=[ChatMessageResponse.model_validate(m) for m in messages],
        )]

    sessions: dict[str, list] = defaultdict(list)
    for msg in messages:
        sessions[msg.session_id].append(msg)

    return [
        MentorHistoryResponse(
            session_id=sid,
            messages=[ChatMessageResponse.model_validate(m) for m in msgs],
        )
        for sid, msgs in sessions.items()
    ]