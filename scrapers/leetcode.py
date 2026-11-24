import requests
from typing import Optional
from models import LeetCodePOTD

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

DAILY_PROBLEM_QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      questionFrontendId
      title
      titleSlug
      difficulty
      topicTags {
        name
        slug
      }
    }
  }
}
"""

def fetch_leetcode_potd() -> Optional[LeetCodePOTD]:
    """Fetches the official LeetCode Problem of the Day."""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://leetcode.com/problemset/all/"
    }
    payload = {"query": DAILY_PROBLEM_QUERY}
    
    try:
        response = requests.post(LEETCODE_GRAPHQL_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        challenge = data.get("data", {}).get("activeDailyCodingChallengeQuestion", {})
        if not challenge:
            return None
            
        date = challenge.get("date")
        link = challenge.get("link")
        question = challenge.get("question", {})
        
        q_id = question.get("questionFrontendId", "")
        title = question.get("title", "")
        title_slug = question.get("titleSlug", "")
        difficulty = question.get("difficulty", "Medium")
        topic_tags = [t["name"] for t in question.get("topicTags", [])]
        
        full_url = f"https://leetcode.com{link}" if link.startswith("/") else link
        
        return LeetCodePOTD(
            date=date,
            question_id=q_id,
            title=title,
            title_slug=title_slug,
            difficulty=difficulty,
            topic_tags=topic_tags,
            url=full_url
        )
    except Exception as e:
        print(f"[LeetCode Scraper Error] {e}")
        return None

if __name__ == "__main__":
    potd = fetch_leetcode_potd()
    if potd:
        print(f"POTD: {potd.question_id}. {potd.title} ({potd.difficulty})")
        print(f"Topics: {', '.join(potd.topic_tags)}")
        print(f"Link: {potd.url}")
    else:
        print("Failed to fetch POTD.")
