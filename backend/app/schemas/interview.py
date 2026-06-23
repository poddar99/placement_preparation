from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InterviewAskRequest(BaseModel):
    question: str = Field(min_length=3)
    company: Optional[str] = None
    role: Optional[str] = None


class InterviewAskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)


class InterviewIngestRequest(BaseModel):
    company: str
    role: str
    experience: str
    outcome: Optional[str] = None
    difficulty: Optional[str] = None


class InterviewIngestResponse(BaseModel):
    id: str
    message: str


class MockInterviewStartRequest(BaseModel):
    focus_areas: Optional[List[str]] = None
    difficulty: Optional[str] = "medium"
    num_questions: Optional[int] = 5


class MockInterviewStartResponse(BaseModel):
    session_id: int
    questions: List[Dict[str, Any]]


class MockInterviewAnswerRequest(BaseModel):
    question_index: int
    answer: str = Field(min_length=1)


class MockInterviewAnswerResponse(BaseModel):
    question_index: int
    score: float
    feedback: str
    session_complete: bool
    overall_score: Optional[float] = None


class MockInterviewSessionResponse(BaseModel):
    id: int
    questions_json: Dict[str, Any]
    scores_json: Optional[Dict[str, Any]] = None
    overall_score: Optional[float] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}