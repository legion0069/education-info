import requests
from typing import List, Set
from models import JobAlert
from database import compute_alert_hash

UNSTOP_API_URL = "https://unstop.com/api/public/opportunity/search-result"

# Flagship Hyderabad Hackathons & Innovation Challenges for Engineering Students
FLAGSHIP_HYDERABAD_EVENTS = [
    {
        "company": "T-Hub Hyderabad",
        "role": "T-Hub National Innovation & AI Hackathon",
        "batch": "2027 / 2026 Engineering Students",
        "eligible_degrees": ["B.Tech", "B.E.", "Dual Degree", "MCA"],
        "eligible_branches": ["All Engineering Branches (CSE, AI, ECE, Mechanical)"],
        "job_type": "Hackathon ➔ Incubation & Pre-Placement Interviews (PPIs)",
        "stipend_or_ctc": "Cash Prize Pool: ₹2,00,000 + T-Hub Incubation Support",
        "location": "📍 T-Hub Phase 2, Raidurg, Knowledge City, Hyderabad",
        "apply_url": "https://t-hub.co/programs/",
        "deadline": "Registration Open (Seasonal Flagship)",
        "source": "T-Hub Official Innovation Portal"
    },
    {
        "company": "IIIT Hyderabad",
        "role": "Megathon (IIIT-H E-Cell Flagship Hackathon)",
        "batch": "2027 Engineering Batch",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech"],
        "eligible_branches": ["Open to All Engineering Students across India"],
        "job_type": "24-Hour National Hackathon",
        "stipend_or_ctc": "Prizes: ₹1,50,000 + Direct Startup Internship PPIs",
        "location": "📍 IIIT Hyderabad Campus, Gachibowli, Hyderabad",
        "apply_url": "https://ecell.iiit.ac.in/",
        "deadline": "Annual National Hackathon (Spring / Fall)",
        "source": "E-Cell IIIT Hyderabad"
    },
    {
        "company": "Google Developer Groups (GDG) Hyderabad",
        "role": "DevFest Hyderabad & Student Solution Challenge",
        "batch": "2027 B.Tech / Computer Science Students",
        "eligible_degrees": ["B.Tech", "B.E.", "BCA", "MCA"],
        "eligible_branches": ["CSE, IT, AI/ML, Cloud & Web Enthusiasts"],
        "job_type": "Tech Conference, Hackathon & Networking Event",
        "stipend_or_ctc": "Mentorship with Google Developer Experts (GDEs) + Goodies",
        "location": "📍 HICC Novotel / Cyber City Convention, Hyderabad",
        "apply_url": "https://gdg.community.dev/gdg-hyderabad/",
        "deadline": "Registration via GDG Community Portal",
        "source": "GDG Hyderabad"
    },
    {
        "company": "Telangana AI Mission (T-AIM)",
        "role": "T-AIM Grand AI Innovation Challenge",
        "batch": "2027 Engineering Students",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech"],
        "eligible_branches": ["AI/ML, Data Science, CSE, IT"],
        "job_type": "Govt of Telangana State AI Challenge",
        "stipend_or_ctc": "Govt Grant: ₹5,00,000 for winning student teams + Pilot Deployments",
        "location": "📍 Hyderabad (Hybrid)",
        "apply_url": "https://taim-gc.in/",
        "deadline": "State Level AI Challenge",
        "source": "Telangana AI Mission & Nasscom"
    }
]

def fetch_unstop_hyderabad_hackathons() -> List[JobAlert]:
    """Fetches live hackathons happening in or hosted by Hyderabad engineering colleges."""
    alerts: List[JobAlert] = []
    seen_urls: Set[str] = set()
    search_terms = ["hyderabad", "iiit hyderabad", "t-hub"]
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    for term in search_terms:
        params = {
            "opportunity": "hackathons",
            "searchTerm": term,
            "per_page": 8
        }
        try:
            res = requests.get(UNSTOP_API_URL, params=params, headers=headers, timeout=10)
            if res.status_code != 200:
                continue
                
            data = res.json().get("data", {}).get("data", [])
            for item in data:
                title = item.get("title", "").strip()
                org = item.get("organisation", {}).get("name", "Hyderabad College / Tech Firm").strip()
                seo_url = item.get("seo_url") or f"https://unstop.com/{item.get('public_url')}"
                
                if not seo_url or seo_url in seen_urls:
                    continue
                seen_urls.add(seo_url)
                
                deadline = item.get("end_date")
                if deadline and "T" in deadline:
                    deadline = deadline.split("T")[0]
                else:
                    deadline = "Registration Closing Soon"
                    
                alert_id = compute_alert_hash("hyd_hackathon", org, title, seo_url)
                alerts.append(
                    JobAlert(
                        job_id=alert_id,
                        company=org,
                        role=f"🏆 {title}",
                        batch="2027 / 2026 Engineering Batch",
                        eligible_degrees=["B.Tech", "B.E.", "MCA", "Dual Degree"],
                        eligible_branches=["All Engineering Streams (Coding, AI, Hardware)"],
                        job_type="Hackathon / Coding Competition",
                        stipend_or_ctc="Cash Prizes + Certificates + PPI Opportunities",
                        location="📍 Hyderabad, Telangana (In-Person / Hybrid)",
                        apply_url=seo_url,
                        deadline=deadline,
                        source="Unstop (Hyderabad Events)"
                    )
                )
        except Exception as e:
            print(f"[Unstop Hyd Hackathons Error for {term}] {e}")
            
    return alerts

def get_all_hyderabad_tech_events() -> List[JobAlert]:
    """Aggregates all flagship and live Hyderabad hackathons & tech events."""
    all_events: List[JobAlert] = []
    
    # 1. Flagship Hyderabad Events (T-Hub, IIIT-H Megathon, GDG, T-AIM)
    for ev in FLAGSHIP_HYDERABAD_EVENTS:
        alert_id = compute_alert_hash("flagship_hyd", ev["company"], ev["role"])
        all_events.append(
            JobAlert(
                job_id=alert_id,
                company=ev["company"],
                role=f"🏆 {ev['role']}",
                batch=ev["batch"],
                eligible_degrees=ev["eligible_degrees"],
                eligible_branches=ev["eligible_branches"],
                job_type=ev["job_type"],
                stipend_or_ctc=ev["stipend_or_ctc"],
                location=ev["location"],
                apply_url=ev["apply_url"],
                deadline=ev["deadline"],
                source=ev["source"]
            )
        )
        
    # 2. Live college hackathons across Hyderabad
    all_events.extend(fetch_unstop_hyderabad_hackathons())
    return all_events

if __name__ == "__main__":
    events = get_all_hyderabad_tech_events()
    print(f"Total Hyderabad Hackathons & Tech Events: {len(events)}")
    for ev in events[:6]:
        print(f"- {ev.role} | {ev.company} | {ev.location}")
        print(f"  Link: {ev.apply_url}")
