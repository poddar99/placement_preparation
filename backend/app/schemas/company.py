from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CompanyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    difficulty_level: str
    hiring_process: Optional[str] = None

    model_config = {"from_attributes": True}


class RoadmapGenerateRequest(BaseModel):
    weeks_available: Optional[int] = 12
    focus_areas: Optional[List[str]] = None


class RoadmapResponse(BaseModel):
    id: int
    company_id: int
    company_name: str
    content_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}