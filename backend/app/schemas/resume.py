from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResumeAnalysisResult(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    suggested_projects: List[str] = Field(default_factory=list)
    score: float = 0.0
    summary: Optional[str] = None


class ResumeReportResponse(BaseModel):
    id: int
    filename: str
    analysis_json: Dict[str, Any]
    score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeRewriteRequest(BaseModel):
    bullet_point: str = Field(min_length=5)
    context: Optional[str] = None


class ResumeRewriteResponse(BaseModel):
    original: str
    rewritten: str
    improvements: List[str] = Field(default_factory=list)