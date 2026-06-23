from datetime import datetime, timezone
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.dsa import DSAProgress, DSATopic, UserStats
from app.models.user import User
from app.schemas.dsa import (
    DSAFullProgressResponse,
    DSAProgressBulkUpdate,
    DSAProgressResponse,
    DSATopicResponse,
    LeetCodeStatsResponse,
    LeetCodeSyncRequest,
)
from app.services.leetcode_service import leetcode_service
from app.services.leetcode_sync_service import (
    build_leetcode_stats_from_user,
    sync_leetcode_profile,
)

router = APIRouter(prefix="/dsa", tags=["DSA Tracker"])


@router.get("/topics", response_model=List[DSATopicResponse])
async def list_topics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(DSATopic).order_by(DSATopic.id))
    return [DSATopicResponse.model_validate(t) for t in result.scalars().all()]


async def _build_progress_response(
    current_user: User,
    db: AsyncSession,
) -> DSAFullProgressResponse:
    topics_result = await db.execute(select(DSATopic))
    topics = {t.id: t for t in topics_result.scalars().all()}

    progress_result = await db.execute(
        select(DSAProgress).where(DSAProgress.user_id == current_user.id)
    )
    progress_map = {p.topic_id: p for p in progress_result.scalars().all()}

    responses: List[DSAProgressResponse] = []
    for topic_id, topic in topics.items():
        prog = progress_map.get(topic_id)
        solved = prog.problems_solved if prog else 0
        pct = (solved / topic.total_problems * 100) if topic.total_problems > 0 else 0
        responses.append(DSAProgressResponse(
            id=prog.id if prog else 0,
            topic_id=topic_id,
            topic_name=topic.name,
            problems_solved=solved,
            total_problems=topic.total_problems,
            proficiency_level=prog.proficiency_level if prog else "beginner",
            last_practiced=prog.last_practiced if prog else None,
            progress_percent=round(pct, 1),
        ))

    stats_result = await db.execute(
        select(UserStats).where(UserStats.user_id == current_user.id)
    )
    stats = stats_result.scalar_one_or_none()

    return DSAFullProgressResponse(
        items=responses,
        contest_rating=stats.contest_rating if stats else 0,
        current_streak=stats.current_streak if stats else 0,
        total_problems_solved=stats.total_problems_solved if stats else 0,
        leetcode=build_leetcode_stats_from_user(current_user, stats),
    )


@router.get("/leetcode/preview/{username}", response_model=LeetCodeStatsResponse)
async def preview_leetcode_profile(
    username: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Fetch LeetCode stats without saving (for preview)."""
    try:
        profile = await leetcode_service.fetch_profile(username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LeetCode fetch failed: {e}")

    return LeetCodeStatsResponse(
        username=profile["username"],
        ranking=profile.get("ranking"),
        total_solved=profile["total_solved"],
        easy_solved=profile["easy_solved"],
        medium_solved=profile["medium_solved"],
        hard_solved=profile["hard_solved"],
        contest_rating=profile["contest_rating"],
        contest_attended=profile["contest_attended"],
        contest_global_ranking=profile.get("contest_global_ranking"),
        contest_top_percentage=profile.get("contest_top_percentage"),
        profile_url=f"https://leetcode.com/u/{profile['username']}/",
        tag_counts=profile.get("tag_counts", {}),
    )


@router.post("/leetcode/sync", response_model=DSAFullProgressResponse)
async def sync_leetcode(
    data: LeetCodeSyncRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch LeetCode profile and sync DSA progress automatically."""
    try:
        await sync_leetcode_profile(db, current_user, data.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LeetCode sync failed: {e}")

    return await _build_progress_response(current_user, db)


@router.get("/progress", response_model=DSAFullProgressResponse)
async def get_progress(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await _build_progress_response(current_user, db)


@router.put("/progress", response_model=DSAFullProgressResponse)
async def update_progress(
    data: DSAProgressBulkUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stats_result = await db.execute(
        select(UserStats).where(UserStats.user_id == current_user.id)
    )
    stats = stats_result.scalar_one_or_none()
    if not stats:
        stats = UserStats(user_id=current_user.id)
        db.add(stats)

    for update in data.updates:
        topic_result = await db.execute(select(DSATopic).where(DSATopic.id == update.topic_id))
        topic = topic_result.scalar_one_or_none()
        if not topic:
            raise HTTPException(status_code=404, detail=f"Topic {update.topic_id} not found")

        prog_result = await db.execute(
            select(DSAProgress).where(
                DSAProgress.user_id == current_user.id,
                DSAProgress.topic_id == update.topic_id,
            )
        )
        prog = prog_result.scalar_one_or_none()

        if not prog:
            prog = DSAProgress(user_id=current_user.id, topic_id=update.topic_id)
            db.add(prog)

        if update.problems_solved is not None:
            prog.problems_solved = update.problems_solved
        if update.proficiency_level is not None:
            prog.proficiency_level = update.proficiency_level
        prog.last_practiced = datetime.now(timezone.utc)

        if update.contest_rating is not None:
            stats.contest_rating = update.contest_rating
        if update.current_streak is not None:
            stats.current_streak = update.current_streak
        if update.total_problems_solved is not None:
            stats.total_problems_solved = update.total_problems_solved

    await db.flush()
    return await _build_progress_response(current_user, db)