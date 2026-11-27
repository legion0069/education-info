import asyncio
from fastapi import FastAPI, HTTPException, Query, Header, BackgroundTasks, Request
from fastapi.responses import PlainTextResponse
from typing import Optional
from telegram import Bot, Update

from config import CRON_SECRET_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID, is_configured
from database import init_db, is_already_sent, mark_as_sent
from scrapers.leetcode import fetch_leetcode_potd
from scrapers.contests import get_all_upcoming_contests
from scrapers.unstop import fetch_unstop_opportunities
from scrapers.exam_tracker import get_national_exams
from scrapers.tier1_tracker import get_tier1_programs
from scrapers.multi_board_scraper import fetch_all_multi_board_opportunities
from scrapers.github_swe_tracker import fetch_github_college_jobs
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
            mark_as_sent(alert_id, "dispatched", f"LeetCode: {potd.title}", potd.url)
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
            mark_as_sent(alert_id, "dispatched", "Upcoming Contests Digest", contests[0].url)

async def task_afternoon():
    """Runs high-volume verified engineering jobs & internships across LinkedIn, Internshala, Instahyre, GitHub & Unstop."""
    if not is_configured():
        return
        
    dispatched_count = 0
    
    # 1. Direct Summer 2027 College Internships from Open-Source Tech Tracker (NVIDIA, Airbnb, Rivian, Palantir, etc.)
    github_jobs = fetch_github_college_jobs(limit=15)
    for g_job in github_jobs:
        if not is_already_sent(g_job.job_id):
            msg = format_job_alert_whatsapp(g_job)
            await send_alert_for_approval(
                bot_token=TELEGRAM_BOT_TOKEN,
                chat_id=TELEGRAM_ADMIN_CHAT_ID,
                alert_id=g_job.job_id,
                title=f"[{g_job.company}] {g_job.role}",
                category="Summer 2027 Intern",
                text=msg,
                url=g_job.apply_url
            )
            mark_as_sent(g_job.job_id, "dispatched", f"{g_job.company} - {g_job.role}", g_job.apply_url)
            dispatched_count += 1
            if dispatched_count >= 4:
                break
                
    # 2. Multi-Board Verified Opportunities (LinkedIn, Internshala, Instahyre)
    multi_jobs = fetch_all_multi_board_opportunities()
    for job in multi_jobs:
        if not is_already_sent(job.job_id):
            msg = format_job_alert_whatsapp(job)
            await send_alert_for_approval(
                bot_token=TELEGRAM_BOT_TOKEN,
                chat_id=TELEGRAM_ADMIN_CHAT_ID,
                alert_id=job.job_id,
                title=f"[{job.source}] {job.company} - {job.role}",
                category=f"{job.source} Opening",
                text=msg,
                url=job.apply_url
            )
            mark_as_sent(job.job_id, "dispatched", f"{job.company} - {job.role}", job.apply_url)
            dispatched_count += 1
            if dispatched_count >= 8:
                break
                
    # 3. Unstop Opportunities
    opportunities = fetch_unstop_opportunities(search_terms=["software", "ai", "developer", "python"], opportunity_type="internships")
    for opp in opportunities:
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
            mark_as_sent(opp.job_id, "dispatched", f"{opp.company} - {opp.role}", opp.apply_url)
            dispatched_count += 1
            if dispatched_count >= 10:
                break

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
            mark_as_sent(ex.job_id, "dispatched", f"{ex.company} - {ex.role}", ex.apply_url)

async def task_tier1():
    """Runs Tier-1 Tech Radar (Google, Amazon, Microsoft, Goldman Sachs, etc.)."""
    if not is_configured():
        return
    programs = get_tier1_programs()
    for prog in programs:
        if not is_already_sent(prog.job_id):
            msg = format_job_alert_whatsapp(prog)
            await send_alert_for_approval(
                bot_token=TELEGRAM_BOT_TOKEN,
                chat_id=TELEGRAM_ADMIN_CHAT_ID,
                alert_id=prog.job_id,
                title=f"Tier-1: {prog.company} - {prog.role}",
                category="Tier-1 Tech Radar",
                text=msg,
                url=prog.apply_url
            )
            mark_as_sent(prog.job_id, "dispatched", f"{prog.company} - {prog.role}", prog.apply_url)

@app.get("/morning")
@app.get("/cron/morning")
async def trigger_morning(token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    verify_token(token, authorization)
    asyncio.create_task(task_morning())
    return PlainTextResponse("OK")

@app.get("/afternoon")
@app.get("/cron/afternoon")
async def trigger_afternoon(token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    verify_token(token, authorization)
    asyncio.create_task(task_afternoon())
    return PlainTextResponse("OK")

@app.get("/evening")
@app.get("/cron/evening")
async def trigger_evening(token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    verify_token(token, authorization)
    asyncio.create_task(task_evening())
    return PlainTextResponse("OK")

@app.get("/tier1")
@app.get("/cron/tier1")
async def trigger_tier1(token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    verify_token(token, authorization)
    asyncio.create_task(task_tier1())
    return PlainTextResponse("OK")

@app.get("/scan")
@app.get("/cron/scan")
@app.get("/all")
@app.get("/cron/all")
async def trigger_all(token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    verify_token(token, authorization)
    asyncio.create_task(task_morning())
    asyncio.create_task(task_afternoon())
    asyncio.create_task(task_evening())
    asyncio.create_task(task_tier1())
    return PlainTextResponse("OK")

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handles incoming Telegram messages (like /scan) and inline button callbacks."""
    if not is_configured():
        return {"status": "ignored", "reason": "not configured"}
    
    try:
        data = await request.json()
    except Exception:
        return {"status": "bad request"}
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # 1. Handle Inline Button Clicks (Mark as Sent / Dismiss)
    if "callback_query" in data:
        cq = data["callback_query"]
        cq_id = cq.get("id")
        data_str = cq.get("data", "")
        msg = cq.get("message", {})
        msg_id = msg.get("message_id")
        chat_id = str(msg.get("chat", {}).get("id", ""))
        original_text = msg.get("text", "")
        
        # Acknowledge callback immediately to remove loading spinner in Telegram
        try:
            await bot.answer_callback_query(callback_query_id=cq_id)
        except Exception as e:
            print(f"Error answering callback: {e}")
            
        if chat_id == TELEGRAM_ADMIN_CHAT_ID and ":" in data_str:
            action, alert_id = data_str.split(":", 1)
            
            if action == "appr":
                mark_as_sent(alert_id, "approved", "Approved Opportunity", "")
                new_text = f"{original_text}\n\n✅ STATUS: APPROVED & RECORDED!"
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=msg_id,
                        text=new_text,
                        reply_markup=None
                    )
                except Exception as e:
                    print(f"Error updating message: {e}")
            elif action == "dism":
                mark_as_sent(alert_id, "dismissed", "Dismissed Opportunity", "")
                new_text = f"{original_text}\n\n❌ STATUS: DISMISSED BY ADMIN."
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=msg_id,
                        text=new_text,
                        reply_markup=None
                    )
                except Exception as e:
                    print(f"Error updating message: {e}")
        return {"status": "ok"}
    
    # 2. Handle Text Messages (/scan, /start)
    if "message" in data:
        msg = data["message"]
        text = msg.get("text", "").strip().lower()
        chat_id = str(msg.get("chat", {}).get("id", ""))
        
        if chat_id == TELEGRAM_ADMIN_CHAT_ID:
            if text in ["/scan", "scan"]:
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text="🔍 *Scan Initiated!*\nChecking LeetCode POTD, Contests, Summer 2027 Internships (NVIDIA, Airbnb), Tier-1 Tech, LinkedIn, Internshala & Instahyre...",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Error sending scan confirmation: {e}")
                background_tasks.add_task(task_morning)
                background_tasks.add_task(task_afternoon)
                background_tasks.add_task(task_evening)
                background_tasks.add_task(task_tier1)
            elif text in ["/start", "start"]:
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text="👋 *2027 Radar Bot is Active!*\n\nSend `/scan` anytime to trigger an instant on-demand scan.",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Error sending start message: {e}")
                    
    return {"status": "ok"}

@app.get("/telegram/setup")
async def setup_telegram_webhook(token: Optional[str] = Query(None)):
    """Registers Render webhook URL with Telegram API."""
    if token != CRON_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not is_configured():
        raise HTTPException(status_code=400, detail="Telegram bot credentials missing")
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    webhook_url = "https://education-info.onrender.com/telegram/webhook"
    success = await bot.set_webhook(url=webhook_url)
    return {"status": "success", "webhook_url": webhook_url, "registered": success}
