import requests
from bs4 import BeautifulSoup
from typing import List
from models import JobAlert
from database import compute_alert_hash

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def fetch_linkedin_jobs(keyword: str = "software intern") -> List[JobAlert]:
    """Scrapes latest Software & AI engineering internships from LinkedIn."""
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={requests.utils.quote(keyword)}&location=India&f_TPR=r86400&start=0"
    alerts: List[JobAlert] = []
    
    try:
        res = requests.get(url, headers=COMMON_HEADERS, timeout=10)
        if res.status_code != 200:
            return alerts
            
        soup = BeautifulSoup(res.text, "html.parser")
        cards = soup.find_all("li")
        
        for c in cards[:5]:
            title_tag = c.find("h3", class_="base-search-card__title")
            comp_tag = c.find("h4", class_="base-search-card__subtitle")
            loc_tag = c.find("span", class_="job-search-card__location")
            link_tag = c.find("a", class_="base-card__full-link")
            
            if not title_tag or not link_tag:
                continue
                
            title = title_tag.text.strip()
            comp = comp_tag.text.strip() if comp_tag else "Confidential / Tech Firm"
            loc = loc_tag.text.strip() if loc_tag else "Pan-India"
            raw_link = link_tag.get("href", "")
            clean_link = raw_link.split("?")[0] if "?" in raw_link else raw_link
            
            alert_id = compute_alert_hash("linkedin", comp, title, clean_link)
            alerts.append(
                JobAlert(
                    job_id=alert_id,
                    company=comp,
                    role=title,
                    batch="2027 / 2026",
                    eligible_degrees=["B.Tech", "B.E.", "MCA", "Dual Degree"],
                    eligible_branches=["CSE", "IT", "AI/ML", "Circuit Branches"],
                    job_type="Internship / Fresher",
                    stipend_or_ctc="As per Company Standards",
                    location=loc,
                    apply_url=clean_link,
                    deadline="Closing Soon (LinkedIn)",
                    source="LinkedIn"
                )
            )
    except Exception as e:
        print(f"[LinkedIn Scraper Error] {e}")
        
    return alerts

def fetch_internshala_internships() -> List[JobAlert]:
    """Scrapes latest Computer Science & Tech internships from Internshala."""
    url = "https://internshala.com/internships/computer-science-internship/"
    alerts: List[JobAlert] = []
    
    try:
        res = requests.get(url, headers=COMMON_HEADERS, timeout=10)
        if res.status_code != 200:
            return alerts
            
        soup = BeautifulSoup(res.text, "html.parser")
        cards = soup.find_all("div", class_="individual_internship")
        
        for c in cards[:5]:
            title_tag = c.find("a", class_="job-title-href")
            comp_tag = c.find("p", class_="company-name")
            stip_tag = c.find("span", class_="stipend")
            
            if not title_tag:
                continue
                
            title = title_tag.text.strip()
            href = title_tag.get("href", "")
            full_link = f"https://internshala.com{href}" if href.startswith("/") else href
            comp = comp_tag.text.strip() if comp_tag else "Startup"
            stipend = stip_tag.text.strip() if stip_tag else "Paid / Unspecified"
            
            alert_id = compute_alert_hash("internshala", comp, title, full_link)
            alerts.append(
                JobAlert(
                    job_id=alert_id,
                    company=comp,
                    role=f"{title} Internship",
                    batch="2027 Engineering & Tech",
                    eligible_degrees=["B.Tech", "B.E.", "BCA", "MCA"],
                    eligible_branches=["CSE", "IT", "AI/ML", "All Interested Students"],
                    job_type="Internship",
                    stipend_or_ctc=stipend,
                    location="Work From Home / Hybrid",
                    apply_url=full_link,
                    deadline="Active on Internshala",
                    source="Internshala"
                )
            )
    except Exception as e:
        print(f"[Internshala Scraper Error] {e}")
        
    return alerts

def fetch_instahyre_jobs() -> List[JobAlert]:
    """Fetches 0-experience software engineering jobs from Instahyre."""
    url = "https://www.instahyre.com/api/v1/job_search?designation=Software%20Engineer&experience=0"
    alerts: List[JobAlert] = []
    
    try:
        res = requests.get(url, headers=COMMON_HEADERS, timeout=10)
        if res.status_code != 200:
            return alerts
            
        data = res.json().get("objects", [])
        for item in data[:4]:
            job_id_num = item.get("id")
            title = item.get("title") or "Software Engineer (Fresher)"
            comp = item.get("employer", {}).get("company_name", "Tech Company")
            locs = item.get("locations") or "Pan-India"
            job_url = f"https://www.instahyre.com/job/{job_id_num}"
            
            alert_id = compute_alert_hash("instahyre", comp, str(job_id_num))
            alerts.append(
                JobAlert(
                    job_id=alert_id,
                    company=comp,
                    role=title,
                    batch="2027 / 2026 Batch",
                    eligible_degrees=["B.Tech", "B.E.", "M.Tech", "MCA"],
                    eligible_branches=["CSE", "IT", "AI/ML", "Software Engineering"],
                    job_type="Full-time / Entry Level",
                    stipend_or_ctc="Competitive Package / High Growth Startup",
                    location=str(locs),
                    apply_url=job_url,
                    deadline="Apply Early",
                    source="Instahyre"
                )
            )
    except Exception as e:
        print(f"[Instahyre Scraper Error] {e}")
        
    return alerts

def fetch_all_multi_board_opportunities() -> List[JobAlert]:
    """Aggregates latest opportunities from LinkedIn, Internshala, and Instahyre."""
    all_jobs: List[JobAlert] = []
    all_jobs.extend(fetch_linkedin_jobs())
    all_jobs.extend(fetch_internshala_internships())
    all_jobs.extend(fetch_instahyre_jobs())
    return all_jobs

if __name__ == "__main__":
    jobs = fetch_all_multi_board_opportunities()
    print(f"Total multi-board jobs fetched: {len(jobs)}")
    for j in jobs[:6]:
        print(f"[{j.source}] {j.company} - {j.role} | {j.apply_url}")
