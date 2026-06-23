from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.interview import MockInterviewSession
from app.models.user import User
from app.schemas.interview import (
    MockInterviewAnswerRequest,
    MockInterviewAnswerResponse,
    MockInterviewSessionResponse,
    MockInterviewStartRequest,
    MockInterviewStartResponse,
)
from app.services.mock_interview_service import mock_interview_service

router = APIRouter(prefix="/mock-interview", tags=["Mock Interview"])


@router.post("/start", response_model=MockInterviewStartResponse)
async def start_mock_interview(
    data: MockInterviewStartRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        questions = await mock_interview_service.generate_questions(
            focus_areas=data.focus_areas,
            difficulty=data.difficulty or "medium",
            num_questions=data.num_questions or 5,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    session = MockInterviewSession(
        user_id=current_user.id,
        questions_json={"questions": questions},
        scores_json={"evaluations": []},
        status="in_progress",
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)

    return MockInterviewStartResponse(session_id=session.id, questions=questions)


@router.post("/{session_id}/answer", response_model=MockInterviewAnswerResponse)
async def submit_answer(
    session_id: int,
    data: MockInterviewAnswerRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(MockInterviewSession).where(
            MockInterviewSession.id == session_id,
            MockInterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Session already completed")

    questions = session.questions_json.get("questions", [])
    if data.question_index < 0 or data.question_index >= len(questions):
        raise HTTPException(status_code=400, detail="Invalid question index")

    question = questions[data.question_index]

    try:
        evaluation = await mock_interview_service.evaluate_answer(question, data.answer)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    scores = session.scores_json or {"evaluations": []}
    evaluations = scores.get("evaluations", [])

    existing = next((e for e in evaluations if e.get("question_index") == data.question_index), None)
    eval_entry = {
        "question_index": data.question_index,
        "answer": data.answer,
        "score": evaluation["score"],
        "feedback": evaluation["feedback"],
        "strengths": evaluation.get("strengths", []),
        "improvements": evaluation.get("improvements", []),
    }

    if existing:
        evaluations.remove(existing)
    evaluations.append(eval_entry)
    scores["evaluations"] = evaluations
    session.scores_json = scores

    answered_indices = {e["question_index"] for e in evaluations}
    session_complete = len(answered_indices) >= len(questions)

    overall_score = None
    if session_complete:
        overall_score = sum(e["score"] for e in evaluations) / len(evaluations)
        session.overall_score = overall_score
        session.status = "completed"

    await db.flush()

    return MockInterviewAnswerResponse(
        question_index=data.question_index,
        score=evaluation["score"],
        feedback=evaluation["feedback"],
        session_complete=session_complete,
        overall_score=overall_score,
    )


@router.get("/sessions", response_model=List[MockInterviewSessionResponse])
async def list_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(MockInterviewSession)
        .where(MockInterviewSession.user_id == current_user.id)
        .order_by(MockInterviewSession.created_at.desc())
    )
    return [MockInterviewSessionResponse.model_validate(s) for s in result.scalars().all()]