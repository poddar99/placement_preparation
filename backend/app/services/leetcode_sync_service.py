from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dsa import DSAProgress, DSATopic, UserStats
from app.models.user import User
from app.schemas.dsa import LeetCodeStatsResponse
from app.services.leetcode_service import leetcode_service


async def sync_leetcode_profile(
    db: AsyncSession,
    user: User,
    username: Optional[str] = None,
) -> tuple[dict, LeetCodeStatsResponse]:
    """
    Fetch LeetCode public profile and sync into user_stats + dsa_progress.
    Returns raw profile data and formatted stats response.
    """
    lc_username = (username or user.leetcode_username or "").strip().lower()
    if not lc_username:
        raise ValueError("LeetCode username not set. Add it in Profile or pass in sync request.")

    profile = await leetcode_service.fetch_profile(lc_username)

    user.leetcode_username = profile["username"]

    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == user.id))
    stats = stats_result.scalar_one_or_none()
    if not stats:
        stats = UserStats(user_id=user.id)
        db.add(stats)

    stats.total_problems_solved = profile["total_solved"]
    stats.contest_rating = profile["contest_rating"]
    stats.leetcode_ranking = profile.get("ranking")
    stats.leetcode_easy = profile["easy_solved"]
    stats.leetcode_medium = profile["medium_solved"]
    stats.leetcode_hard = profile["hard_solved"]
    stats.leetcode_contest_attended = profile["contest_attended"]
    stats.leetcode_last_synced = datetime.now(timezone.utc)
    stats.leetcode_sync_data = profile

    topics_result = await db.execute(select(DSATopic))
    topics_by_name = {t.name: t for t in topics_result.scalars().all()}

    progress_result = await db.execute(
        select(DSAProgress).where(DSAProgress.user_id == user.id)
    )
    progress_map = {p.topic_id: p for p in progress_result.scalars().all()}

    for topic_name, solved_count in profile["topic_progress"].items():
        topic = topics_by_name.get(topic_name)
        if not topic:
            continue

        prog = progress_map.get(topic.id)
        if not prog:
            prog = DSAProgress(user_id=user.id, topic_id=topic.id)
            db.add(prog)
            progress_map[topic.id] = prog

        prog.problems_solved = solved_count
        prog.proficiency_level = leetcode_service.proficiency_from_count(solved_count)
        prog.last_practiced = datetime.now(timezone.utc)

    await db.flush()

    stats_response = LeetCodeStatsResponse(
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
        last_synced=stats.leetcode_last_synced,
        profile_url=f"https://leetcode.com/u/{profile['username']}/",
        tag_counts=profile.get("tag_counts", {}),
    )

    return profile, stats_response


def build_leetcode_stats_from_user(user: User, stats: Optional[UserStats]) -> Optional[LeetCodeStatsResponse]:
    if not user.leetcode_username or not stats or not stats.leetcode_last_synced:
        return None

    sync_data = stats.leetcode_sync_data or {}
    return LeetCodeStatsResponse(
        username=user.leetcode_username,
        ranking=stats.leetcode_ranking,
        total_solved=stats.total_problems_solved,
        easy_solved=stats.leetcode_easy,
        medium_solved=stats.leetcode_medium,
        hard_solved=stats.leetcode_hard,
        contest_rating=stats.contest_rating,
        contest_attended=stats.leetcode_contest_attended,
        contest_global_ranking=sync_data.get("contest_global_ranking"),
        contest_top_percentage=sync_data.get("contest_top_percentage"),
        last_synced=stats.leetcode_last_synced,
        profile_url=f"https://leetcode.com/u/{user.leetcode_username}/",
        tag_counts=sync_data.get("tag_counts", {}),
    )