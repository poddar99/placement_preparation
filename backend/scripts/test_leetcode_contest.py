import httpx
import json

query = """
query userContestRanking($username: String!) {
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    topPercentage
  }
}
"""

r = httpx.post(
    "https://leetcode.com/graphql",
    json={"query": query, "variables": {"username": "soumyapoddar16"}},
    timeout=30,
)
print(json.dumps(r.json(), indent=2))