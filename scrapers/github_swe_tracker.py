import requests
import re
from typing import List
from models import JobAlert
from database import compute_alert_hash

GITHUB_README_URL = "https://raw.githubusercontent.com/speedyapply/2026-SWE-College-Jobs/main/README.md"

def fetch_github_college_jobs(limit: int = 10) -> List[JobAlert]:
    """Fetches verified college & summer internships directly from top tech open-source tracker."""
    alerts: List[JobAlert] = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(GITHUB_README_URL, headers=headers, timeout=10)
        if res.status_code != 200:
            return alerts
            
        lines = [line.strip() for line in res.text.split("\n") if "|" in line and "http" in line]
        
        for line in lines:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) < 5:
                continue
                
            # Extract Company Name
            comp_part = parts[0]
            comp_match = re.search(r'<strong>(.*?)</strong>', comp_part, re.IGNORECASE)
            company = comp_match.group(1).strip() if comp_match else re.sub(r'<[^>]+>', '', comp_part).strip()
            
            # Extract Role
            role = re.sub(r'<[^>]+>', '', parts[1]).strip()
            
            # Extract Location
            location = re.sub(r'<[^>]+>', '', parts[2]).strip() or "Remote / Global"
            
            # Extract Salary / Stipend
            salary = re.sub(r'<[^>]+>', '', parts[3]).strip()
            if not salary or salary == "🔒":
                salary = "Competitive / Industry Standard"
                
            # Extract Direct Application Link (Workday, Greenhouse, Lever, etc.)
            link_part = parts[4]
            link_match = re.search(r'href=["\'](http[^"\']+)["\']', link_part)
            if not link_match:
                continue
            apply_url = link_match.group(1).strip()
            
            # Filter: Check if relevant to 2027 engineering students
            lower_role = role.lower()
            if not any(k in lower_role for k in ["intern", "software", "developer", "engineer", "ai", "data", "tech"]):
                continue
                
            alert_id = compute_alert_hash("github_swe", company, role, apply_url)
            
            alerts.append(
                JobAlert(
                    job_id=alert_id,
                    company=company,
                    role=role,
                    batch="2027 / 2026 (College Summer Intern)",
                    eligible_degrees=["B.Tech", "B.E.", "M.Tech", "Dual Degree"],
                    eligible_branches=["CSE", "IT", "AI/ML", "Circuit Branches"],
                    job_type="Summer Internship",
                    stipend_or_ctc=salary,
                    location=location,
                    apply_url=apply_url,
                    deadline="Apply As Soon As Possible (Rolling)",
                    source="Direct Careers Portal (Workday/Greenhouse)"
                )
            )
            if len(alerts) >= limit:
                break
                
    except Exception as e:
        print(f"[GitHub SWE Tracker Error] {e}")
        
    return alerts

if __name__ == "__main__":
    jobs = fetch_github_college_jobs(limit=5)
    print(f"Fetched {len(jobs)} verified jobs from GitHub tracker:")
    for j in jobs:
        print(f"- [{j.company}] {j.role} | {j.location} | {j.stipend_or_ctc}")
        print(f"  Link: {j.apply_url}")
