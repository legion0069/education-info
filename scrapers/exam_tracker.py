from typing import List
from models import JobAlert
from database import compute_alert_hash

# Verified registry of National Qualifier Tests & Campus Hiring programs targeting 2027 batch
EXAM_RECORDS = [
    {
        "company": "Tata Consultancy Services (TCS)",
        "role": "TCS National Qualifier Test (NQT 2027) - Ninja, Digital & Prime",
        "batch": "2027 Batch (Pre-Final / Final Year)",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech", "MCA", "M.Sc (CS/IT)"],
        "eligible_branches": ["CSE", "IT", "AI/DS", "ECE", "EEE", "All Engineering Streams"],
        "job_type": "National Level Hiring Exam",
        "stipend_or_ctc": "Ninja: ₹3.36 LPA | Digital: ₹7.0 LPA | Prime: ₹9.0 - ₹11.5 LPA",
        "location": "Pan-India (TCS iON Test Centres & Remote)",
        "apply_url": "https://www.tcs.com/careers/india/tcs-national-qualifier-test",
        "deadline": "Active Registration Window",
        "source": "TCS Official Careers Portal"
    },
    {
        "company": "Deloitte US-India",
        "role": "Deloitte National Level Assessment (NLA 2027) - Associate Analyst",
        "batch": "2027 Passouts",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech"],
        "eligible_branches": ["CSE", "IT", "AI", "Software Engg", "Circuit Branches"],
        "job_type": "National Level Hiring Exam",
        "stipend_or_ctc": "₹4.50 LPA - ₹7.60 LPA + Performance Bonus",
        "location": "Hyderabad, Bengaluru, Gurugram, Mumbai, Pune",
        "apply_url": "https://usindiacareers.deloitte.com/chp",
        "deadline": "Check College Placement Cell / Official Portal",
        "source": "Deloitte USI Careers"
    },
    {
        "company": "Infosys",
        "role": "HackWithInfy & Specialist Programmer (SP / DSE 2027)",
        "batch": "2027 Batch",
        "eligible_degrees": ["B.Tech", "B.E.", "M.Tech", "MCA"],
        "eligible_branches": ["All Engineering Branches (Coding Based)"],
        "job_type": "National Coding Competition / Hiring",
        "stipend_or_ctc": "Specialist Programmer: ₹9.5 LPA | DSE: ₹6.25 LPA | Systems Eng: ₹3.6 LPA",
        "location": "Pan-India",
        "apply_url": "https://infyspringboard.onwingspan.com/",
        "deadline": "Announced via Springboard",
        "source": "Infosys Springboard"
    },
    {
        "company": "Accenture",
        "role": "Associate Software Engineer (ASE) & Advanced ASE",
        "batch": "2027 Engineering Batch",
        "eligible_degrees": ["B.Tech", "B.E.", "MCA"],
        "eligible_branches": ["CSE", "IT", "AI", "ECE", "Mechanical", "Civil (All Streams)"],
        "job_type": "Campus & Off-Campus Assessment",
        "stipend_or_ctc": "ASE: ₹4.50 LPA | AASE: ₹6.50 LPA",
        "location": "Pan-India Tech Delivery Centres",
        "apply_url": "https://india.accenture.com/campus",
        "deadline": "Rolling Applications",
        "source": "Accenture Careers India"
    },
    {
        "company": "Cognizant",
        "role": "Cognizant GenC, GenC Elevate & GenC Next",
        "batch": "2027 Batch",
        "eligible_degrees": ["B.Tech", "B.E.", "MCA"],
        "eligible_branches": ["CSE", "IT", "AI/ML", "ECE", "Circuital"],
        "job_type": "National Campus Hiring Drive",
        "stipend_or_ctc": "GenC: ₹4.0 LPA | GenC Elevate: ₹5.4 LPA | GenC Next: ₹6.75 - ₹9.0 LPA",
        "location": "Bengaluru, Chennai, Pune, Hyderabad, Kolkata",
        "apply_url": "https://careers.cognizant.com/global-en/campus/",
        "deadline": "Campus Specific / National Drive",
        "source": "Cognizant Campus"
    }
]

def get_national_exams() -> List[JobAlert]:
    alerts: List[JobAlert] = []
    for ex in EXAM_RECORDS:
        alert_id = compute_alert_hash("exam", ex["company"], ex["role"])
        alerts.append(
            JobAlert(
                job_id=alert_id,
                company=ex["company"],
                role=ex["role"],
                batch=ex["batch"],
                eligible_degrees=ex["eligible_degrees"],
                eligible_branches=ex["eligible_branches"],
                job_type=ex["job_type"],
                stipend_or_ctc=ex["stipend_or_ctc"],
                location=ex["location"],
                apply_url=ex["apply_url"],
                deadline=ex["deadline"],
                source=ex["source"]
            )
        )
    return alerts

if __name__ == "__main__":
    exams = get_national_exams()
    print(f"Loaded {len(exams)} National Exam Tracks:")
    for e in exams:
        print(f"- {e.company}: {e.role} | CTC: {e.stipend_or_ctc}")
