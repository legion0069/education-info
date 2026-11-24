import asyncio
from fastapi import FastAPI, HTTPException, Query, Header, BackgroundTasks
from typing import Optional

from config import CRON_SECRET_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID, is_configured
from database import init_db, is_already_sent, mark_as_sent
from scrapers.leetcode import fetch_leetcode_potd
from scrapers.contests import get_all_upcoming_contests
from scrapers.unstop import fetch_unstop_opportunities
from scrapers.exam_tracker import get_national_exams
from formatter import (
    format_leetcode_potd_whatsapp,
    format_contests_whatsapp,
    format_job_alert_whatsapp
)
from telegram_dispatcher import send_alert_for_approval

app = FastAPI(
    title="2027 Placements & Internship Radar API",
    description="Automated Scraper & Dispatcher for 2027 Engineering Batch",
    version="1.0.0"
)

init_db()

def verify_token(token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    """Verifies secret token from cron-jobs.org query param or Authorization header."""
    auth_header_token = None
    if authorization and authorization.startswith("Bearer "):
        auth_header_token = authorization.split(" ")[1]
    
    provided = token or auth_header_token
    if not provided or provided != CRON_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid cron secret token")

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "2027 Placements & Internship Engine",
        "telegram_configured": is_configured()
    }

async def task_morning():
    """Runs LeetCode POTD and Contest Digest."""
    if not is_configured():
        return
    # 1. LeetCode POTD
    potd = fetch_leetcode_potd()
    if potd:
        alert_id = f"leetcode_potd_{potd.date}"
        if not is_already_sent(alert_id):
            msg = format_leetcode_potd_whatsapp(potd)
            await send_alert_for_approval(
                bot_token=TELEGRAM_BOT_TOKEN,
                chat_id=TELEGRAM_ADMIN_CHAT_ID,
                alert_id=alert_id,
                title=f"LeetCode: {potd.title}",
                category="DSA Challenge",
                text=msg,
                url=potd.url
            )
    # 2. Contests
    contests = get_all_upcoming_contests()
    if contests:
        alert_id = f"contests_digest_{contests[0].name}_{contests[0].start_time[:6]}"
        if not is_already_sent(alert_id):
            msg = format_contests_whatsapp(contests[:4])
            await send_alert_for_approval(
                bot_token=TELEGRAM_BOT_TOKEN,
                chat_id=TELEGRAM_ADMIN_CHAT_ID,
                alert_id=alert_id,
                title="Upcoming Coding Contests",
                category="Contest Radar",
                text=msg,
                url=contests[0].url
            )

async def task_afternoon():
    """Runs Tech Internships & Opportunities from Unstop."""
    if not is_configured():
        return
    opportunities = fetch_unstop_opportunities(search_terms=["software", "ai", "developer"], opportunity_type="internships")
    for opp in opportunities[:3]:
        if not is_already_sent(opp.job_id):
            msg = format_job_alert_whatsapp(opp)
            await send_alert_for_approval(
                bot_token=TELEGRAM_BOT_TOKEN,
                chat_id=TELEGRAM_ADMIN_CHAT_ID,
                alert_id=opp.job_id,
                title=f"{opp.company} - {opp.role}",
                category="Tech Internship",
                text=msg,
                url=opp.apply_url
            )

async def task_evening():
    """Runs National Level Exams (TCS NQT, Deloitte NLA, Infosys, etc.)."""
    if not is_configured():
        return
    exams = get_national_exams()
    for ex in exams:
        if not is_already_sent(ex.job_id):
            msg = format_job_alert_whatsapp(ex)
            await send_alert_for_approval(
                bot_token=TELEGRAM_BOT_TOKEN,
                chat_id=TELEGRAM_ADMIN_CHAT_ID,
                alert_id=ex.job_id,
                title=f"{ex.company} - {ex.role}",
                category="National Exam",
                text=msg,
                url=ex.apply_url
            )

@app.get("/morning")
@app.get("/cron/morning")
async def trigger_morning(background_tasks: BackgroundTasks, token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    verify_token(token, authorization)
    background_tasks.add_task(task_morning)
    return {"status": "success", "triggered": "morning_schedule (LeetCode POTD + Contests)"}

@app.get("/afternoon")
@app.get("/cron/afternoon")
async def trigger_afternoon(background_tasks: BackgroundTasks, token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    verify_token(token, authorization)
    background_tasks.add_task(task_afternoon)
    return {"status": "success", "triggered": "afternoon_schedule (Tech Internships)"}

@app.get("/evening")
@app.get("/cron/evening")
async def trigger_evening(background_tasks: BackgroundTasks, token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    verify_token(token, authorization)
    background_tasks.add_task(task_evening)
    return {"status": "success", "triggered": "evening_schedule (National Exams & Drives)"}

@app.get("/all")
@app.get("/cron/all")
async def trigger_all(background_tasks: BackgroundTasks, token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    verify_token(token, authorization)
    background_tasks.add_task(task_morning)
    background_tasks.add_task(task_afternoon)
    background_tasks.add_task(task_evening)
    return {"status": "success", "triggered": "full_scan_pipeline"}
