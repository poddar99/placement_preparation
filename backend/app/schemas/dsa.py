from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DSATopicResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    total_problems: int

    model_config = {"from_attributes": True}


class DSAProgressResponse(BaseModel):
    id: int
    topic_id: int
    topic_name: str
    problems_solved: int
    total_problems: int = 0
    proficiency_level: str
    last_practiced: Optional[datetime] = None
    progress_percent: float = 0.0

    model_config = {"from_attributes": True}


class DSAProgressUpdate(BaseModel):
    topic_id: int
    problems_solved: Optional[int] = None
    proficiency_level: Optional[str] = None
    contest_rating: Optional[int] = None
    current_streak: Optional[int] = None
    total_problems_solved: Optional[int] = None


class DSAProgressBulkUpdate(BaseModel):
    updates: List[DSAProgressUpdate] = Field(default_factory=list)


class LeetCodeSyncRequest(BaseModel):
    username: Optional[str] = Field(
        default=None,
        description="LeetCode username. Uses profile username if omitted.",
    )


class LeetCodeStatsResponse(BaseModel):
    username: str
    ranking: Optional[int] = None
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    contest_rating: int = 0
    contest_attended: int = 0
    contest_global_ranking: Optional[int] = None
    contest_top_percentage: Optional[float] = None
    current_streak: int = 0
    last_synced: Optional[datetime] = None
    profile_url: str = ""
    tag_counts: Dict[str, int] = Field(default_factory=dict)


class DSAFullProgressResponse(BaseModel):
    items: List[DSAProgressResponse]
    contest_rating: int = 0
    current_streak: int = 0
    total_problems_solved: int = 0
    leetcode: Optional[LeetCodeStatsResponse] = None