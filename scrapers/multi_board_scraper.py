import requests
from bs4 import BeautifulSoup
from typing import List, Set
from models import JobAlert
from database import compute_alert_hash

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Strict Engineering Keywords (Real Tech / Coding / AI Roles Only)
TECH_KEYWORDS = [
    "software", "sde", "developer", "engineer", "frontend", "backend",
    "full stack", "fullstack", "ai", "ml", "machine learning", "data",
    "python", "java", "react", "node", "cloud", "devops", "android",
    "ios", "web development", "intern", "qa", "system", "embedded"
]

SPAM_KEYWORDS = [
    "sales", "telecaller", "bpo", "content writer", "data entry",
    "graphic design", "video edit", "marketing", "hr intern", "human resources",
    "tele-calling", "cold calling", "business development associate", "bda"
]

# Primary Geographic Focus: Bangalore, Hyderabad & Remote / WFH
TARGET_LOCATIONS = ["bangalore", "bengaluru", "hyderabad", "remote", "wfh", "work from home", "hybrid"]

def is_target_location(loc: str) -> bool:
    """Verifies that the location is Bangalore, Hyderabad, or Remote/WFH."""
    if not loc:
        return False
    loc_lower = loc.lower()
    return any(city in loc_lower for city in TARGET_LOCATIONS)

def is_legit_tech_role(title: str) -> bool:
    """Verifies that the job title is a genuine software/engineering opportunity and not spam."""
    title_lower = title.lower()
    if any(s in title_lower for s in SPAM_KEYWORDS):
        return False
    return any(t in title_lower for t in TECH_KEYWORDS)

def format_clean_location(loc: str) -> str:
    """Standardizes location display with emojis for student bulletins."""
    loc_lower = loc.lower()
    if "hyderabad" in loc_lower:
        return "🏙️ Hyderabad, Telangana"
    elif "bangalore" in loc_lower or "bengaluru" in loc_lower:
        return "🏙️ Bangalore (Bengaluru), Karnataka"
    elif any(r in loc_lower for r in ["remote", "wfh", "work from home"]):
        return "🏠 Remote / Work From Home"
    return loc

def fetch_linkedin_hyd_blr_jobs() -> List[JobAlert]:
    """Scrapes latest Software & AI engineering internships in Bangalore and Hyderabad from LinkedIn."""
    city_configs = [
        ("Bengaluru%2C%20Karnataka%2C%20India", "Bangalore"),
        ("Hyderabad%2C%20Telangana%2C%20India", "Hyderabad")
    ]
    queries = ["software intern", "sde intern", "2027 intern", "ai intern"]
    
    alerts: List[JobAlert] = []
    seen_urls: Set[str] = set()
    
    for city_encoded, city_label in city_configs:
        for q in queries:
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={requests.utils.quote(q)}&location={city_encoded}&f_TPR=r604800&start=0"
            try:
                res = requests.get(url, headers=COMMON_HEADERS, timeout=10)
                if res.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(res.text, "html.parser")
                cards = soup.find_all("li")
                
                for c in cards:
                    title_tag = c.find("h3", class_="base-search-card__title")
                    comp_tag = c.find("h4", class_="base-search-card__subtitle")
                    loc_tag = c.find("span", class_="job-search-card__location")
                    link_tag = c.find("a", class_="base-card__full-link")
                    
                    if not title_tag or not link_tag:
                        continue
                        
                    title = title_tag.text.strip()
                    if not is_legit_tech_role(title):
                        continue
                        
                    raw_link = link_tag.get("href", "")
                    clean_link = raw_link.split("?")[0] if "?" in raw_link else raw_link
                    if clean_link in seen_urls:
                        continue
                    seen_urls.add(clean_link)
                    
                    comp = comp_tag.text.strip() if comp_tag else "Tech Enterprise"
                    raw_loc = loc_tag.text.strip() if loc_tag else city_label
                    clean_loc = format_clean_location(raw_loc)
                    
                    alert_id = compute_alert_hash("linkedin", comp, title, clean_link)
                    alerts.append(
                        JobAlert(
                            job_id=alert_id,
                            company=comp,
                            role=title,
                            batch="2027 / 2026 Batch",
                            eligible_degrees=["B.Tech", "B.E.", "MCA", "Dual Degree"],
                            eligible_branches=["CSE", "IT", "AI/ML", "Circuit Branches"],
                            job_type="Internship / Fresher Role",
                            stipend_or_ctc="As per Industry Standards (Paid)",
                            location=clean_loc,
                            apply_url=clean_link,
                            deadline="Apply Early (Active on LinkedIn)",
                            source=f"LinkedIn ({city_label})"
                        )
                    )
            except Exception as e:
                print(f"[LinkedIn Scraper Error for {city_label} - {q}] {e}")
                
    return alerts

def fetch_internshala_hyd_blr_internships() -> List[JobAlert]:
    """Scrapes verified tech internships specifically in Bangalore, Hyderabad, and Remote from Internshala."""
    routes = [
        ("computer-science-internship-in-bangalore", "Bangalore"),
        ("computer-science-internship-in-hyderabad", "Hyderabad"),
        ("artificial-intelligence-ai-internship-in-bangalore", "Bangalore"),
        ("artificial-intelligence-ai-internship-in-hyderabad", "Hyderabad"),
        ("work-from-home-computer-science-internships", "Remote")
    ]
    alerts: List[JobAlert] = []
    seen_urls: Set[str] = set()
    
    for route, city_label in routes:
        url = f"https://internshala.com/internships/{route}/"
        try:
            res = requests.get(url, headers=COMMON_HEADERS, timeout=10)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.find_all("div", class_="individual_internship")
            
            for c in cards:
                title_tag = c.find("a", class_="job-title-href")
                comp_tag = c.find("p", class_="company-name")
                stip_tag = c.find("span", class_="stipend")
                
                if not title_tag:
                    continue
                    
                title = title_tag.text.strip()
                if not is_legit_tech_role(title):
                    continue
                    
                href = title_tag.get("href", "")
                full_link = f"https://internshala.com{href}" if href.startswith("/") else href
                if full_link in seen_urls:
                    continue
                seen_urls.add(full_link)
                
                comp = comp_tag.text.strip() if comp_tag else "Tech Startup"
                stipend = stip_tag.text.strip() if stip_tag else "Paid Stipend"
                clean_loc = format_clean_location(city_label)
                
                alert_id = compute_alert_hash("internshala", comp, title, full_link)
                alerts.append(
                    JobAlert(
                        job_id=alert_id,
                        company=comp,
                        role=f"{title} Internship",
                        batch="2027 Engineering Students",
                        eligible_degrees=["B.Tech", "B.E.", "BCA", "MCA"],
                        eligible_branches=["CSE", "IT", "AI/ML", "Circuit Branches"],
                        job_type="Internship",
                        stipend_or_ctc=stipend,
                        location=clean_loc,
                        apply_url=full_link,
                        deadline="Active on Internshala",
                        source=f"Internshala ({city_label})"
                    )
                )
        except Exception as e:
            print(f"[Internshala Error for {route}] {e}")
            
    return alerts

def fetch_instahyre_hyd_blr_jobs() -> List[JobAlert]:
    """Fetches verified 0-experience software engineering openings in Bangalore and Hyderabad from Instahyre."""
    url = "https://www.instahyre.com/api/v1/job_search?designation=Software%20Engineer&experience=0"
    alerts: List[JobAlert] = []
    
    try:
        res = requests.get(url, headers=COMMON_HEADERS, timeout=10)
        if res.status_code != 200:
            return alerts
            
        data = res.json().get("objects", [])
        for item in data:
            locs_raw = str(item.get("locations") or "")
            if not is_target_location(locs_raw):
                continue
                
            job_id_num = item.get("id")
            title = item.get("title") or "Software Engineer (Fresher)"
            if not is_legit_tech_role(title):
                continue
                
            comp = item.get("employer", {}).get("company_name", "Tech Startup")
            clean_loc = format_clean_location(locs_raw)
            job_url = f"https://www.instahyre.com/job/{job_id_num}"
            
            alert_id = compute_alert_hash("instahyre", comp, str(job_id_num))
            alerts.append(
                JobAlert(
                    job_id=alert_id,
                    company=comp,
                    role=title,
                    batch="2027 / 2026 Batch",
                    eligible_degrees=["B.Tech", "B.E.", "M.Tech", "MCA"],
                    eligible_branches=["CSE", "IT", "AI/ML", "Circuit Branches"],
                    job_type="Full-time / Entry Level",
                    stipend_or_ctc="Competitive Startup Package",
                    location=clean_loc,
                    apply_url=job_url,
                    deadline="Apply Early",
                    source="Instahyre (Hyd/Blr)"
                )
            )
    except Exception as e:
        print(f"[Instahyre Error] {e}")
        
    return alerts

def fetch_all_multi_board_opportunities() -> List[JobAlert]:
    """Aggregates all legit opportunities in Hyderabad, Bangalore & Remote."""
    all_jobs: List[JobAlert] = []
    all_jobs.extend(fetch_linkedin_hyd_blr_jobs())
    all_jobs.extend(fetch_internshala_hyd_blr_internships())
    all_jobs.extend(fetch_instahyre_hyd_blr_jobs())
    return all_jobs

if __name__ == "__main__":
    jobs = fetch_all_multi_board_opportunities()
    print(f"Total Hyderabad & Bangalore tech openings fetched: {len(jobs)}")
    for j in jobs[:8]:
        print(f"[{j.source}] {j.company} - {j.role} | {j.location} | {j.apply_url}")
