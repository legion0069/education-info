from typing import List
from models import JobAlert
from database import compute_alert_hash

# High-Yield Post-Graduation Pathways for 2027 B.Tech CSE / IT / AI / Engineering Students
HIGHER_STUDIES_PROGRAMS = [
    {
        "company": "GATE (IITs, IISc & PSUs)",
        "role": "M.Tech / MS Research (IISc, IITs, NITs) & PSU Direct Recruitment",
        "batch": "2027 Passouts (Pre-Final Year Eligible for GATE)",
        "eligible_degrees": ["B.Tech", "B.E.", "MCA", "Dual Degree"],
        "eligible_branches": ["CSE", "DA (Data Science & AI)", "ECE", "All Disciplines"],
        "job_type": "M.Tech / MS (Research) / PSU Scientist",
        "stipend_or_ctc": "MHRD Scholarship: ₹12,400/mo (M.Tech) | ₹37,000/mo (PhD) | PSU CTC: ₹14 - ₹22 LPA",
        "location": "Top IITs, IISc Bangalore, NITs, Central PSUs",
        "apply_url": "https://gate.iitk.ac.in/",
        "deadline": "Registration opens Aug-Sept | Exam in Feb",
        "source": "GATE Official Organizing Institute"
    },
    {
        "company": "MS in CS / AI Abroad (USA, Germany, Ireland)",
        "role": "Master of Science (MS in Computer Science / Artificial Intelligence)",
        "batch": "2027 Batch (Fall Intake Target)",
        "eligible_degrees": ["B.Tech", "B.E."],
        "eligible_branches": ["CSE", "IT", "AI/ML", "Circuit Branches"],
        "job_type": "International Master's Degree (STEM Designated)",
        "stipend_or_ctc": "Average Tech Post-Grad Salary: $105,000 - $135,000 / year (USA) | €65,000 / year (Germany)",
        "location": "USA, Germany (Tuition-Free Universities via DAAD), Ireland, UK",
        "apply_url": "https://www.daad.de/en/study-and-research-in-germany/",
        "deadline": "GRE / TOEFL Prep: 3rd Year | Fall Applications: Sept - Dec",
        "source": "Global University Portals / DAAD Germany"
    },
    {
        "company": "CAT & Tech MBA (IIMs & Top Business Schools)",
        "role": "MBA in Business Analytics, Product Management & IT Operations",
        "batch": "2027 Batch",
        "eligible_degrees": ["B.Tech", "B.E.", "Graduation (Any Stream)"],
        "eligible_branches": ["All Engineering Disciplines"],
        "job_type": "Post Graduate Diploma in Management (PGDM / MBA)",
        "stipend_or_ctc": "Average IIM / Top B-School CTC: ₹22.0 - ₹34.0 LPA",
        "location": "IIM Ahmedabad, Bangalore, Calcutta, Lucknow, FMS, SPJIMR",
        "apply_url": "https://iimcat.ac.in/",
        "deadline": "Registration: Aug - Sept | Exam: Last Sunday of November",
        "source": "IIM CAT Organizing Committee"
    },
    {
        "company": "ISRO & DRDO Technical Recruitment",
        "role": "Scientist / Engineer 'SC' (Government Research & Space Technology)",
        "batch": "2027 Batch",
        "eligible_degrees": ["B.Tech", "B.E. (First Class with min 65% or 6.84 CGPA)"],
        "eligible_branches": ["Computer Science, Electronics & Comm, Mechanical"],
        "job_type": "Gazetted Central Govt Post (Group 'A')",
        "stipend_or_ctc": "Level 10 Pay Matrix: ₹56,100/mo Basic (~₹90,000/mo in-hand + Quarters & Govt Perks)",
        "location": "ISRO Centers (VSSC, URSC, SAC) / DRDO Labs across India",
        "apply_url": "https://www.isro.gov.in/Careers.html",
        "deadline": "Annual Notification via ISRO ICRB & DRDO RAC",
        "source": "ISRO Centralised Recruitment Board (ICRB)"
    },
    {
        "company": "IIIT Hyderabad PGEE & BITS HD",
        "role": "M.Tech in Computer Science & Information Security / MS by Research in AI",
        "batch": "2027 Batch",
        "eligible_degrees": ["B.Tech", "B.E.", "MCA"],
        "eligible_branches": ["CSE, IT, AI, Math & Computing"],
        "job_type": "Post-Graduate Specialized Tech Degree",
        "stipend_or_ctc": "Average Placement Package: ₹28.5 - ₹32.0 LPA (At par with top IITs)",
        "location": "IIIT Hyderabad / BITS Pilani, Goa, Hyderabad",
        "apply_url": "https://pgadmissions.iiit.ac.in/pgee/",
        "deadline": "Applications Open: Feb - March | Exam: April - May",
        "source": "IIIT-H PG Admissions"
    }
]

def get_higher_studies_programs() -> List[JobAlert]:
    alerts: List[JobAlert] = []
    for prog in HIGHER_STUDIES_PROGRAMS:
        alert_id = compute_alert_hash("higher_studies", prog["company"], prog["role"])
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
    pathways = get_higher_studies_programs()
    print(f"Loaded {len(pathways)} Post-Graduation Pathways:")
    for p in pathways:
        print(f"- [{p.company}] {p.role} | Benefits: {p.stipend_or_ctc}")
