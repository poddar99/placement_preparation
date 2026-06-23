import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# Primary LeetCode tag per PlacementPilot topic (no summing — tags overlap heavily)
TOPIC_PRIMARY_TAG: Dict[str, str] = {
    "Arrays": "Array",
    "Strings": "String",
    "Linked Lists": "Linked List",
    "Stacks & Queues": "Stack",
    "Trees": "Tree",
    "Graphs": "Depth-First Search",
    "Dynamic Programming": "Dynamic Programming",
    "Greedy": "Greedy",
    "Binary Search": "Binary Search",
    "Heaps": "Heap",
}

PROFILE_QUERY = """
query userPublicProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats: submitStatsGlobal {
      acSubmissionNum { difficulty count submissions }
    }
    profile { ranking reputation starRating userAvatar ranking }
    tagProblemCounts {
      advanced { tagName problemsSolved }
      intermediate { tagName problemsSolved }
      fundamental { tagName problemsSolved }
    }
  }
}
"""

CONTEST_QUERY = """
query userContestRanking($username: String!) {
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    topPercentage
  }
}
"""

class LeetCodeService:
    """Fetches public LeetCode profile data via the official GraphQL API."""

    def __init__(self) -> None:
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def _graphql(self, query: str, variables: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                LEETCODE_GRAPHQL_URL,
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()

        if payload.get("errors"):
            messages = [e.get("message", "Unknown error") for e in payload["errors"]]
            raise ValueError(f"LeetCode API error: {'; '.join(messages)}")

        return payload.get("data", {})

    async def fetch_profile(self, username: str) -> Dict[str, Any]:
        username = username.strip().lower()
        if not username:
            raise ValueError("LeetCode username is required")

        profile_data = await self._graphql(PROFILE_QUERY, {"username": username})
        matched = profile_data.get("matchedUser")
        if not matched:
            raise ValueError(f"LeetCode user '{username}' not found")

        contest_data: Dict[str, Any] = {}
        try:
            contest_result = await self._graphql(CONTEST_QUERY, {"username": username})
            contest_data = contest_result.get("userContestRanking") or {}
        except Exception as exc:
            logger.warning("Could not fetch contest data for %s: %s", username, exc)

        tag_counts = self._parse_tag_counts(matched.get("tagProblemCounts", {}))
        submit_stats = self._parse_submit_stats(matched.get("submitStats", {}))
        topic_progress = self._map_tags_to_topics(tag_counts)

        return {
            "username": matched["username"],
            "ranking": matched.get("profile", {}).get("ranking"),
            "reputation": matched.get("profile", {}).get("reputation", 0),
            "star_rating": matched.get("profile", {}).get("starRating"),
            "avatar": matched.get("profile", {}).get("userAvatar"),
            "total_solved": submit_stats.get("All", 0),
            "easy_solved": submit_stats.get("Easy", 0),
            "medium_solved": submit_stats.get("Medium", 0),
            "hard_solved": submit_stats.get("Hard", 0),
            "contest_rating": int(contest_data.get("rating", 0)) if contest_data.get("rating") else 0,
            "contest_attended": contest_data.get("attendedContestsCount", 0),
            "contest_global_ranking": contest_data.get("globalRanking"),
            "contest_top_percentage": contest_data.get("topPercentage"),
            "tag_counts": tag_counts,
            "topic_progress": topic_progress,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }

    def _parse_submit_stats(self, submit_stats: dict) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for entry in submit_stats.get("acSubmissionNum", []):
            result[entry.get("difficulty", "")] = entry.get("count", 0)
        return result

    def _parse_tag_counts(self, tag_problem_counts: dict) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for level in ("fundamental", "intermediate", "advanced"):
            for tag in tag_problem_counts.get(level, []) or []:
                name = tag.get("tagName", "")
                solved = tag.get("problemsSolved", 0)
                if name:
                    counts[name] = counts.get(name, 0) + solved
        return counts

    def _map_tags_to_topics(self, tag_counts: Dict[str, int]) -> Dict[str, int]:
        """Map each PlacementPilot topic to its primary LeetCode tag count."""
        return {
            topic_name: tag_counts.get(primary_tag, 0)
            for topic_name, primary_tag in TOPIC_PRIMARY_TAG.items()
        }

    @staticmethod
    def proficiency_from_count(solved: int) -> str:
        if solved >= 26:
            return "advanced"
        if solved >= 11:
            return "intermediate"
        if solved >= 1:
            return "beginner"
        return "beginner"


leetcode_service = LeetCodeService()