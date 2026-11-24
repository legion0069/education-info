# 🚀 2027 Placement & Internships Automated Feed

An automated intelligence pipeline designed for **2027 Engineering (B.Tech CSE / IT / AI / ECE)** students. It collects, cleans, and formats high-value placement drives, national exams, tech internships, and daily DSA challenges into ready-to-post WhatsApp community announcements.

---

## 📂 Project Structure

```
2027 info/
├── .venv/                     # Python 3.12 Virtual Environment
├── models.py                  # Pydantic schemas (LeetCodePOTD, CodingContest, JobAlert)
├── database.py                # SQLite deduplication engine (alerts.db)
├── formatter.py               # WhatsApp message templates (bolding, emojis, tags)
├── main.py                    # Orchestrator & CLI runner
├── requirements.txt           # Project dependencies
└── scrapers/
    ├── __init__.py
    ├── leetcode.py            # Official LeetCode GraphQL POTD scraper
    ├── contests.py            # Upcoming contest tracker (LeetCode, Codeforces in IST)
    ├── unstop.py              # Live Unstop tech internships & fresher drive scraper
    └── exam_tracker.py        # TCS NQT 2027, Deloitte NLA 2027, Infosys, Cognizant, Accenture
```

---

## 🛠 Features Implemented

1. **LeetCode Problem of the Day (POTD)**:
   - Fetches today's live problem via LeetCode's GraphQL API.
   - Extracts difficulty (`Easy`, `Medium`, `Hard`), problem number, and topic tags (`Sliding Window`, `Greedy`, `Graphs`, etc.).

2. **Coding Contest Radar**:
   - Fetches upcoming LeetCode Weekly/Biweekly rounds and Codeforces contests.
   - Automatically converts start times to **Indian Standard Time (IST)** with duration.

3. **National Level Exams for 2027 Batch**:
   - **TCS NQT 2027**: Ninja (₹3.36 LPA), Digital (₹7 LPA), Prime (₹9 - ₹11.5 LPA).
   - **Deloitte NLA 2027**: Associate Analyst (₹4.5 - ₹7.6 LPA).
   - **Infosys HackWithInfy / SP / DSE 2027**: (₹3.6 - ₹9.5 LPA).
   - **Accenture & Cognizant GenC / Elevate**: Campus & Off-Campus assessment tracks.

4. **Live Tech Internships & Opportunities**:
   - Queries Unstop's live opportunities endpoint for software, AI, developer internships with stipend amounts and direct application URLs.

5. **SQLite Deduplication**:
   - Computes unique SHA-256 hashes of alerts.
   - Ensures your WhatsApp community **never receives duplicate posts**!

---

## 🚀 How to Run

### Dry Run (Preview messages without saving to DB)
```bash
.\.venv\Scripts\python.exe main.py
```

### Live Run (Marks sent items into `alerts.db`)
```bash
.\.venv\Scripts\python.exe main.py --live
```
