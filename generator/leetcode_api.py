"""Fetch public LeetCode stats from leetcode.com's GraphQL endpoint."""
import datetime as dt
import json
import urllib.request

ENDPOINT = "https://leetcode.com/graphql"
QUERY = ("query($u:String!){matchedUser(username:$u){"
         "submitStatsGlobal{acSubmissionNum{difficulty count}} userCalendar{submissionCalendar}} "
         "allQuestionsCount{difficulty count}}")


def request(user):
    """The raw `data` object LeetCode returns for `user`."""
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"query": QUERY, "variables": {"u": user}}).encode(),
        headers={"content-type": "application/json", "referer": "https://leetcode.com",
                 "user-agent": "Mozilla/5.0 (profile-readme-builder)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def by_difficulty(entries):
    """[{difficulty, count}, ...] → {"All"|"Easy"|"Medium"|"Hard": count}."""
    return {e["difficulty"]: e["count"] for e in entries}


def calendar(raw):
    """LeetCode's {"<unix seconds>": count} JSON string → {UTC date: count}."""
    return {dt.datetime.fromtimestamp(int(k), dt.timezone.utc).date(): v for k, v in json.loads(raw).items()}


def parse(data):
    """Reduce the raw response to {solved, total, cal}."""
    user = data["matchedUser"]
    return dict(solved=by_difficulty(user["submitStatsGlobal"]["acSubmissionNum"]),
                total=by_difficulty(data["allQuestionsCount"]),
                cal=calendar(user["userCalendar"]["submissionCalendar"]))


def fetch(user):
    """Stats for `user`. Raises on any network or format error."""
    return parse(request(user))
