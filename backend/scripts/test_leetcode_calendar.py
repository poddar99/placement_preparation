import httpx
import json
from datetime import datetime

query = """
query userCalendar($username: String!, $year: Int!) {
  matchedUser(username: $username) {
    userCalendar(year: $year) {
      submissionCalendar
    }
  }
}
"""

r = httpx.post(
    "https://leetcode.com/graphql",
    json={"query": query, "variables": {"username": "soumyapoddar16", "year": datetime.now().year}},
    timeout=30,
)
data = r.json()
cal = data.get("data", {}).get("matchedUser", {}).get("userCalendar", {})
print("keys:", cal.keys() if cal else "none")
if cal.get("submissionCalendar"):
    import base64
    # submissionCalendar is often a compressed/base64 string - LeetCode returns JSON string
    raw = cal["submissionCalendar"]
    print("type:", type(raw), "sample:", str(raw)[:200])