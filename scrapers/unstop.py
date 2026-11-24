import requests
from typing import List
from models import JobAlert
from database import compute_alert_hash

UNSTOP_API_URL = "https://unstop.com/api/public/opportunity/search-result"

def fetch_unstop_opportunities(search_terms: List[str] = None, opportunity_type: str = "internships") -> List[JobAlert]:
    """
    Fetches tech internships or fresher jobs from Unstop.
    opportunity_type: 'internships', 'jobs', 'hackathons'
    """
    if search_terms is None:
        search_terms = ["software", "developer", "data science", "ai", "python"]
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
        "Accept": "application/json"
    }
    
    alerts: List[JobAlert] = []
    seen_ids = set()
    
    for term in search_terms:
        params = {
            "opportunity": opportunity_type,
            "searchTerm": term,
            "per_page": 10
        }
        try:
            res = requests.get(UNSTOP_API_URL, params=params, headers=headers, timeout=10)
            if res.status_code != 200:
                continue
            
            data = res.json().get("data", {}).get("data", [])
            for item in data:
                item_id = str(item.get("id"))
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                
                title = item.get("title", "").strip()
                org = item.get("organisation", {}).get("name", "Unknown Organization").strip()
                seo_url = item.get("seo_url") or f"https://unstop.com/{item.get('public_url')}"
                
                # Extract salary/stipend info
                job_detail = item.get("jobDetail") or {}
                min_sal = job_detail.get("min_salary")
                max_sal = job_detail.get("max_salary")
                pay_in = job_detail.get("pay_in", "monthly")
                
                stipend = "Not Disclosed / As per Industry Standards"
                if min_sal and max_sal:
                    stipend = f"₹{min_sal:,} - ₹{max_sal:,} / {pay_in}"
                elif min_sal:
                    stipend = f"₹{min_sal:,} / {pay_in}"
                    
                locations_raw = item.get("locations", [])
                loc_names = []
                for l in locations_raw:
                    if isinstance(l, str):
                        loc_names.append(l)
                    elif isinstance(l, dict):
                        city = l.get("city") or l.get("name") or l.get("location")
                        if city:
                            loc_names.append(str(city))
                loc_str = ", ".join(loc_names) if loc_names else "Pan-India / Remote"
                
                deadline = item.get("end_date")
                if deadline and "T" in deadline:
                    deadline = deadline.split("T")[0]
                    
                alert_id = compute_alert_hash("unstop", item_id, title)
                
                alerts.append(
                    JobAlert(
                        job_id=alert_id,
                        company=org,
                        role=title,
                        batch="2027 / 2026",
                        eligible_degrees=["B.Tech", "B.E.", "MCA", "Dual Degree"],
                        eligible_branches=["CSE", "IT", "AI/ML", "ECE", "Circuit Branches"],
                        job_type="Internship" if opportunity_type == "internships" else "Full-time / Drive",
                        stipend_or_ctc=stipend,
                        location=loc_str,
                        apply_url=seo_url,
                        deadline=deadline or "Closing Soon",
                        source="Unstop"
                    )
                )
        except Exception as e:
            print(f"[Unstop Scraper Error for {term}] {e}")
            
    return alerts

if __name__ == "__main__":
    jobs = fetch_unstop_opportunities(search_terms=["software", "ai"], opportunity_type="internships")
    print(f"Fetched {len(jobs)} opportunities from Unstop:")
    for j in jobs[:5]:
        print(f"- {j.company} | {j.role} | {j.stipend_or_ctc} | {j.apply_url}")
