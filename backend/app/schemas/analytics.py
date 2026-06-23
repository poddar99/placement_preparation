from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TopicAnalytics(BaseModel):
    topic_name: str
    progress_percent: float
    problems_solved: int
    total_problems: int


class AnalyticsResponse(BaseModel):
    dsa_completion_percent: float
    strong_areas: List[str]
    weak_areas: List[str]
    readiness_score: float
    topic_breakdown: List[TopicAnalytics]
    cs_subjects: List[Dict[str, Any]]
    resume_score: Optional[float] = None
    mock_interview_avg: Optional[float] = None
    llm_insights: Optional[str] = None