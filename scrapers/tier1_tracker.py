from typing import List
from models import JobAlert
from database import compute_alert_hash

# Verified Tier-1 Tech Flagship Hiring & Internship Programs for 2027 Engineering Batch
TIER1_PROGRAMS = [
    {
        "company": "Google",
        "role": "Software Engineering Summer Intern / STEP Intern (2027)",
        "batch": "2027 Batch (B.Tech / B.E. / Dual Degree)",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech", "Dual Degree"],
        "eligible_branches": ["CSE", "IT", "AI/ML", "Data Science", "Circuit Branches"],
        "job_type": "Summer Internship (PPO Eligible)",
        "stipend_or_ctc": "₹1,10,000 - ₹1,35,000 / month + Relocation & Perks",
        "location": "Bengaluru, Hyderabad",
        "apply_url": "https://www.google.com/about/careers/applications/jobs/results/?q=Software%20Engineer%20Intern",
        "deadline": "Rolling Applications / Seasonal Window",
        "source": "Google Students Careers Portal"
    },
    {
        "company": "Amazon",
        "role": "Amazon WOW (Women in Tech) & SDE Summer Intern 2027",
        "batch": "2027 Batch (2nd / Pre-Final Year)",
        "eligible_degrees": ["B.Tech", "B.E.", "MCA", "M.Tech"],
        "eligible_branches": ["All Engineering Disciplines (CSE/IT preferred)"],
        "job_type": "Summer Internship / PPO Track",
        "stipend_or_ctc": "₹80,000 - ₹1,10,000 / month + ₹45 LPA FTE PPO Target",
        "location": "Bengaluru, Hyderabad, Chennai, Pune",
        "apply_url": "https://amazonwowindia.splashthat.com/",
        "deadline": "Registration Window Active on Amazon WOW Portal",
        "source": "Amazon Student Programs"
    },
    {
        "company": "Microsoft",
        "role": "Software Engineering Intern - Summer 2027",
        "batch": "2027 Passouts",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech"],
        "eligible_branches": ["CSE", "IT", "AI", "ECE", "Mathematics & Computing"],
        "job_type": "Summer Internship (2 Months)",
        "stipend_or_ctc": "₹1,25,000 / month + Housing Stipend",
        "location": "Bengaluru, Hyderabad, Noida",
        "apply_url": "https://careers.microsoft.com/v2/global/en/home.html",
        "deadline": "Check Portal / College Placement Cell",
        "source": "Microsoft University Careers"
    },
    {
        "company": "Goldman Sachs",
        "role": "Engineering Campus Hiring Program (ECHP 2027)",
        "batch": "2027 Batch (Pre-Final Year Students)",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech", "Dual Degree"],
        "eligible_branches": ["All Engineering Branches (Coding Based Assessment)"],
        "job_type": "Summer Analyst (Direct PPO Track)",
        "stipend_or_ctc": "₹1,00,000 / month (FTE Package: ₹24.0 - ₹30.0 LPA)",
        "location": "Bengaluru, Hyderabad",
        "apply_url": "https://www.goldmansachs.com/careers/students/programs/india/engineering-campus-hiring-program.html",
        "deadline": "Announced Seasonally (Aptitude + Math + Advanced DSA)",
        "source": "Goldman Sachs Student Programs"
    },
    {
        "company": "Flipkart",
        "role": "Flipkart GRiD (Software Development Challenge & Hiring)",
        "batch": "2027 & 2026 Batch",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech"],
        "eligible_branches": ["Open to All Engineering Branches"],
        "job_type": "Hackathon ➔ Direct SDE Internship & PPO",
        "stipend_or_ctc": "₹1,00,000 / month Stipend (PPO: ₹32.0 LPA)",
        "location": "Bengaluru (Hybrid)",
        "apply_url": "https://unstop.com/hackathons/flipkart-grid",
        "deadline": "Annual National Challenge on Unstop",
        "source": "Flipkart Campus Relations"
    },
    {
        "company": "Uber",
        "role": "Uber Software Engineer Intern & Uber She++",
        "batch": "2027 Passouts",
        "eligible_degrees": ["B.Tech", "B.E."],
        "eligible_branches": ["CSE, IT, AI, Circuit Branches"],
        "job_type": "Summer Internship",
        "stipend_or_ctc": "₹1,60,000 / month + Comprehensive Benefits",
        "location": "Bengaluru, Hyderabad",
        "apply_url": "https://www.uber.com/us/en/careers/",
        "deadline": "Check University Openings on Uber Careers",
        "source": "Uber University Recruiting"
    },
    {
        "company": "Atlassian",
        "role": "Associate Software Engineer / Intern 2027",
        "batch": "2027 Batch",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech"],
        "eligible_branches": ["CSE, IT, AI/ML, Software Systems"],
        "job_type": "Summer Internship (Remote-First)",
        "stipend_or_ctc": "₹1,00,000 / month (FTE Package: ₹50.0+ LPA CTC)",
        "location": "Work From Anywhere (India)",
        "apply_url": "https://www.atlassian.com/company/careers/students",
        "deadline": "Rolling Seasonal Hiring",
        "source": "Atlassian University Talent"
    }
]

def get_tier1_programs() -> List[JobAlert]:
    alerts: List[JobAlert] = []
    for prog in TIER1_PROGRAMS:
        alert_id = compute_alert_hash("tier1", prog["company"], prog["role"])
        alerts.append(
            JobAlert(
                job_id=alert_id,
                company=prog["company"],
                role=prog["role"],
                batch=prog["batch"],
                eligible_degrees=prog["eligible_degrees"],
                eligible_branches=prog["eligible_branches"],
                job_type=prog["job_type"],
                stipend_or_ctc=prog["stipend_or_ctc"],
                location=prog["location"],
                apply_url=prog["apply_url"],
                deadline=prog["deadline"],
                source=prog["source"]
            )
        )
    return alerts

if __name__ == "__main__":
    tier1 = get_tier1_programs()
    print(f"Loaded {len(tier1)} Tier-1 Flagship Programs:")
    for t in tier1:
        print(f"- [{t.company}] {t.role} | Stipend: {t.stipend_or_ctc}")
