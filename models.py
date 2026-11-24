from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class LeetCodePOTD(BaseModel):
    date: str
    question_id: str
    title: str
    title_slug: str
    difficulty: str  # Easy, Medium, Hard
    topic_tags: List[str] = Field(default_factory=list)
    url: str

class CodingContest(BaseModel):
    platform: str  # LeetCode, Codeforces, CodeChef, AtCoder
    name: str
    url: str
    start_time: str
    duration_minutes: int

class JobAlert(BaseModel):
    job_id: str  # Unique hash or portal ID
    company: str
    role: str
    batch: str = "2027"  # Target batch
    eligible_degrees: List[str] = Field(default_factory=lambda: ["B.Tech", "B.E.", "M.Tech", "MCA"])
    eligible_branches: List[str] = Field(default_factory=lambda: ["CSE", "IT", "AI/ML", "ECE", "All Branches"])
    job_type: str = "Internship"  # Internship, Full-time, NQT / NLA Exam
    stipend_or_ctc: Optional[str] = "Not Disclosed"
    location: str = "Pan-India / Remote"
    apply_url: str
    deadline: Optional[str] = "Not Specified"
    source: str
    posted_date: Optional[str] = None
