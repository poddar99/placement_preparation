from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MentorChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: Optional[str] = None


class MentorChatResponse(BaseModel):
    session_id: str
    reply: str


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    session_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MentorHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageResponse]