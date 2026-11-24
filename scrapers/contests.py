import requests
from datetime import datetime, timezone, timedelta
from typing import List
from models import CodingContest

IST = timezone(timedelta(hours=5, minutes=30))

def fetch_leetcode_contests() -> List[CodingContest]:
    """Fetches upcoming LeetCode Weekly and Biweekly contests."""
    url = "https://leetcode.com/graphql"
    query = """
    {
      allContests {
        title
        titleSlug
        startTime
        duration
        isVirtual
      }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    contests: List[CodingContest] = []
    try:
        res = requests.post(url, json={"query": query}, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json().get("data", {}).get("allContests", [])
        now_ts = datetime.now(timezone.utc).timestamp()
        
        for c in data:
            start_ts = c.get("startTime", 0)
            if start_ts > now_ts and not c.get("isVirtual", False):
                dt_ist = datetime.fromtimestamp(start_ts, tz=IST)
                contests.append(
                    CodingContest(
                        platform="LeetCode",
                        name=c.get("title"),
                        url=f"https://leetcode.com/contest/{c.get('titleSlug')}",
                        start_time=dt_ist.strftime("%d %b %Y, %I:%M %p IST"),
                        duration_minutes=int(c.get("duration", 5400) / 60)
                    )
                )
    except Exception as e:
        print(f"[LeetCode Contest Error] {e}")
    return contests

def fetch_codeforces_contests() -> List[CodingContest]:
    """Fetches upcoming Codeforces rounds."""
    url = "https://codeforces.com/api/contest.list?gym=false"
    contests: List[CodingContest] = []
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("status") == "OK":
            for c in data.get("result", []):
                # phase "BEFORE" means upcoming
                if c.get("phase") == "BEFORE":
                    start_ts = c.get("startTimeSeconds", 0)
                    dt_ist = datetime.fromtimestamp(start_ts, tz=IST)
                    contests.append(
                        CodingContest(
                            platform="Codeforces",
                            name=c.get("name"),
                            url=f"https://codeforces.com/contest/{c.get('id')}",
                            start_time=dt_ist.strftime("%d %b %Y, %I:%M %p IST"),
                            duration_minutes=int(c.get("durationSeconds", 7200) / 60)
                        )
                    )
    except Exception as e:
        print(f"[Codeforces Contest Error] {e}")
    # Return sorted by upcoming date
    return sorted(contests, key=lambda x: x.start_time)

def get_all_upcoming_contests() -> List[CodingContest]:
    all_contests = []
    all_contests.extend(fetch_leetcode_contests())
    all_contests.extend(fetch_codeforces_contests()[:3])  # Top 3 upcoming Codeforces
    return all_contests

if __name__ == "__main__":
    upcoming = get_all_upcoming_contests()
    print(f"Found {len(upcoming)} upcoming contests:")
    for c in upcoming:
        print(f"- [{c.platform}] {c.name} | Start: {c.start_time} ({c.duration_minutes} mins)")
