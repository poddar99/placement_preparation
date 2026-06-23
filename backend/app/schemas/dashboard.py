from typing import List, Optional

from pydantic import BaseModel


class CSSubjectProgressItem(BaseModel):
    subject_name: str
    progress_percent: float


class UpcomingCompany(BaseModel):
    id: int
    name: str
    difficulty_level: str
    description: Optional[str] = None


class DashboardResponse(BaseModel):
    dsa_progress_percent: float
    cs_subjects_progress: List[CSSubjectProgressItem]
    resume_score: Optional[float] = None
    mock_interview_score: Optional[float] = None
    contest_rating: int = 0
    current_streak: int = 0
    total_problems_solved: int = 0
    readiness_score: float = 0.0
    upcoming_companies: List[UpcomingCompany]