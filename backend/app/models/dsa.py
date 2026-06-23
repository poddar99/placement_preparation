from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class DSATopic(Base):
    __tablename__ = "dsa_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    total_problems: Mapped[int] = mapped_column(Integer, default=0)

    progress_entries: Mapped[list["DSAProgress"]] = relationship(back_populates="topic")


class DSAProgress(Base):
    __tablename__ = "dsa_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("dsa_topics.id", ondelete="CASCADE"), nullable=False)
    problems_solved: Mapped[int] = mapped_column(Integer, default=0)
    proficiency_level: Mapped[str] = mapped_column(String(50), default="beginner")
    last_practiced: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="dsa_progress")
    topic: Mapped["DSATopic"] = relationship(back_populates="progress_entries")


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    contest_rating: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    total_problems_solved: Mapped[int] = mapped_column(Integer, default=0)
    leetcode_ranking: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    leetcode_easy: Mapped[int] = mapped_column(Integer, default=0)
    leetcode_medium: Mapped[int] = mapped_column(Integer, default=0)
    leetcode_hard: Mapped[int] = mapped_column(Integer, default=0)
    leetcode_contest_attended: Mapped[int] = mapped_column(Integer, default=0)
    leetcode_last_synced: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    leetcode_sync_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="user_stats")