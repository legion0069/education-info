from models import LeetCodePOTD, CodingContest, JobAlert
from config import WHATSAPP_INVITE_LINK

def get_community_footer() -> str:
    if WHATSAPP_INVITE_LINK:
        return (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📢 *Forward to your batchmates!*\n"
            f"👥 *Join 2027 Community:* {WHATSAPP_INVITE_LINK}"
        )
    return (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 *Share with your batchmates!*\n"
        f"👥 *2027 Engineering & AI Network*"
    )

def format_leetcode_potd_whatsapp(potd: LeetCodePOTD) -> str:
    """Formats LeetCode Problem of the Day for WhatsApp Community with bolding & emojis."""
    diff_emoji = {
        "Easy": "🟢 *Easy*",
        "Medium": "🟡 *Medium*",
        "Hard": "🔴 *Hard*"
    }.get(potd.difficulty, f"*{potd.difficulty}*")
    
    tags_str = ", ".join([f"`{t}`" for t in potd.topic_tags]) if potd.topic_tags else "`DSA`"
    
    message = (
        f"⚡ *LEETCODE DAILY CHALLENGE | {potd.date}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 *Problem:* {potd.question_id}. {potd.title}\n"
        f"📊 *Difficulty:* {diff_emoji}\n"
        f"🏷 *Key Topics:* {tags_str}\n\n"
        f"🎯 *Goal:* Solve this before midnight to keep your LeetCode streak alive!\n\n"
        f"🔗 *Solve Here:*\n{potd.url}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *2027 Tech & Placements Community*"
    )
    return message

def format_contests_whatsapp(contests: list[CodingContest]) -> str:
    """Formats upcoming contests list for WhatsApp."""
    lines = [
        "🏆 *UPCOMING CODING CONTESTS (IST)*",
        "━━━━━━━━━━━━━━━━━━━━━━\n"
    ]
    for c in contests:
        lines.append(
            f"🔹 *[{c.platform}] {c.name}*\n"
            f"   🗓 *Start:* {c.start_time}\n"
            f"   ⏱ *Duration:* {c.duration_minutes} mins\n"
            f"   🔗 *Link:* {c.url}\n"
        )
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 *Tip:* Rating contests are heavily valued during resume shortlisting!\n👥 *2027 Tech Community*")
    return "\n".join(lines)

def format_higher_studies_whatsapp(pathway: JobAlert) -> str:
    """Formats higher education and post-grad career pathways for WhatsApp."""
    degrees = ", ".join(pathway.eligible_degrees)
    branches = ", ".join(pathway.eligible_branches)
    
    message = (
        f"🎓 *HIGHER STUDIES & CAREER PATHWAY | 2027 BATCH*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏛 *Path / Exam:* {pathway.company}\n"
        f"🎯 *Program:* *{pathway.role}*\n"
        f"📅 *Target Batch:* {pathway.batch}\n"
        f"💰 *Stipend / Package:* {pathway.stipend_or_ctc}\n"
        f"📍 *Institutes / Scope:* {pathway.location}\n\n"
        f"📋 *Eligibility & Streams:*\n"
        f"• *Degree:* {degrees}\n"
        f"• *Eligible Branches:* {branches}\n"
        f"• *Track:* {pathway.job_type}\n"
        f"⏳ *Key Dates & Timeline:* {pathway.deadline}\n\n"
        f"🔗 *Official Portal / Guidelines:*\n{pathway.apply_url}\n\n"
        f"{get_community_footer()}"
    )
    return message

def format_job_alert_whatsapp(job: JobAlert) -> str:
    """Formats job or internship drive into clean WhatsApp bulletin."""
    degrees = ", ".join(job.eligible_degrees)
    branches = ", ".join(job.eligible_branches)
    
    header_tag = "🚨 *HIRING ALERT: 2027 BATCH*" if "2027" in job.batch else "🚨 *OPPORTUNITY ALERT*"
    
    message = (
        f"{header_tag}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏢 *Company:* {job.company}\n"
        f"💼 *Role:* {job.role}\n"
        f"🎓 *Target Batch:* *{job.batch}*\n"
        f"💰 *CTC / Stipend:* {job.stipend_or_ctc}\n"
        f"📍 *Location:* {job.location}\n\n"
        f"📋 *Eligibility Criteria:*\n"
        f"• *Degree:* {degrees}\n"
        f"• *Branches:* {branches}\n"
        f"• *Type:* {job.job_type}\n"
        f"⏳ *Deadline:* {job.deadline}\n\n"
        f"🔗 *Direct Application Link:*\n{job.apply_url}\n\n"
        f"{get_community_footer()}"
    )
    return message
