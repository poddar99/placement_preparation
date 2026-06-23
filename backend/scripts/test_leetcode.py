import httpx
import json

query = """
query userPublicProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats: submitStatsGlobal {
      acSubmissionNum { difficulty count submissions }
    }
    profile { ranking reputation starRating }
    tagProblemCounts {
      advanced { tagName problemsSolved }
      intermediate { tagName problemsSolved }
      fundamental { tagName problemsSolved }
    }
  }
}
"""

r = httpx.post(
    "https://leetcode.com/graphql",
    json={"query": query, "variables": {"username": "soumyapoddar16"}},
    timeout=30,
)
print(json.dumps(r.json(), indent=2))