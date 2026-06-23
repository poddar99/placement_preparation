from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    college: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    target_companies: Optional[List[str]] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    target_companies: Optional[List[str]] = None
    leetcode_username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    college: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    target_companies: Optional[List[str]] = None
    leetcode_username: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse