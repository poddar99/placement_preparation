from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.dsa import DSAProgress, UserStats
    from app.models.company import Roadmap
    from app.models.resume import ResumeReport
    from app.models.chat import ChatMessage
    from app.models.interview import MockInterviewSession, CSSubjectProgress


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    college: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_companies: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    leetcode_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    dsa_progress: Mapped[List["DSAProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    user_stats: Mapped[Optional["UserStats"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    roadmaps: Mapped[List["Roadmap"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    resume_reports: Mapped[List["ResumeReport"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    chat_messages: Mapped[List["ChatMessage"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    mock_interview_sessions: Mapped[List["MockInterviewSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    cs_subject_progress: Mapped[List["CSSubjectProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")