import argparse
import asyncio
import sys
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID, is_configured
from database import init_db, is_already_sent, mark_as_sent
from scrapers.leetcode import fetch_leetcode_potd
from scrapers.contests import get_all_upcoming_contests
from scrapers.unstop import fetch_unstop_opportunities
from scrapers.exam_tracker import get_national_exams
from scrapers.tier1_tracker import get_tier1_programs
from scrapers.multi_board_scraper import fetch_all_multi_board_opportunities
from scrapers.github_swe_tracker import fetch_github_college_jobs
from scrapers.hyderabad_events_tracker import get_all_hyderabad_tech_events
from formatter import (
    format_leetcode_potd_whatsapp,
    format_contests_whatsapp,
    format_job_alert_whatsapp
)
from telegram_dispatcher import send_alert_for_approval

async def run_pipeline_async(dry_run: bool = True):
    print("🚀 [1/5] Initializing Database & Tracking...")
    init_db()
    
    can_dispatch_telegram = is_configured()
    if can_dispatch_telegram:
        print(f"📡 Telegram Admin Bot Configured: Ready to deliver to Chat ID {TELEGRAM_ADMIN_CHAT_ID}")
    else:
        print("ℹ️ Telegram credentials not found in .env (running in local preview mode)")

    # 1. LeetCode POTD
    print("\n🧠 [2/5] Checking LeetCode Daily Challenge...")
    potd = fetch_leetcode_potd()
    if potd:
        alert_id = f"leetcode_potd_{potd.date}"
        if not is_already_sent(alert_id):
            print("  ✨ New LeetCode POTD Found!")
            msg = format_leetcode_potd_whatsapp(potd)
            if can_dispatch_telegram and not dry_run:
                try:
                    await send_alert_for_approval(
                        bot_token=TELEGRAM_BOT_TOKEN,
                        chat_id=TELEGRAM_ADMIN_CHAT_ID,
                        alert_id=alert_id,
                        title=f"LeetCode: {potd.title}",
                        category="DSA Challenge",
                        text=msg,
                        url=potd.url
                    )
                    print("  📨 Dispatched to your Telegram for 1-Tap Approval!")
                except Exception as e:
                    print(f"  ❌ Telegram dispatch failed: {e}")
            else:
                print("\n--- [WHATSAPP PREVIEW: LEETCODE POTD] ---\n" + msg + "\n----------------------------------------")
        else:
            print(f"  ⏭ POTD for {potd.date} was already posted/approved.")

    # 2. Upcoming Contests
    print("\n🏆 [3/5] Checking Coding Contests...")
    contests = get_all_upcoming_contests()
    if contests:
        alert_id = f"contests_digest_{contests[0].name}_{contests[0].start_time[:6]}"
        if not is_already_sent(alert_id):
            print(f"  ✨ Found {len(contests)} upcoming contests.")
            msg = format_contests_whatsapp(contests[:4])
            if can_dispatch_telegram and not dry_run:
                try:
                    await send_alert_for_approval(
                        bot_token=TELEGRAM_BOT_TOKEN,
                        chat_id=TELEGRAM_ADMIN_CHAT_ID,
                        alert_id=alert_id,
                        title="Upcoming Coding Contests",
                        category="Contest Radar",
                        text=msg,
                        url=contests[0].url
                    )
                    print("  📨 Dispatched contest digest to Telegram!")
                except Exception as e:
                    print(f"  ❌ Telegram dispatch failed: {e}")
            else:
                print("\n--- [WHATSAPP PREVIEW: CONTEST DIGEST] ---\n" + msg + "\n-----------------------------------------")
        else:
            print("  ⏭ Latest contest digest was already sent/approved.")

    # 3. National Hiring Exams (TCS NQT, Deloitte NLA, etc.)
    print("\n🏢 [4/5] Checking 2027 National Level Hiring Exams...")
    exams = get_national_exams()
    new_exams_count = 0
    for ex in exams:
        if not is_already_sent(ex.job_id):
            new_exams_count += 1
            print(f"  ✨ New Exam Drive: {ex.company} - {ex.role}")
            msg = format_job_alert_whatsapp(ex)
            if can_dispatch_telegram and not dry_run:
                try:
                    await send_alert_for_approval(
                        bot_token=TELEGRAM_BOT_TOKEN,
                        chat_id=TELEGRAM_ADMIN_CHAT_ID,
                        alert_id=ex.job_id,
                        title=f"{ex.company} - {ex.role}",
                        category="National Exam",
                        text=msg,
                        url=ex.apply_url
                    )
                    print(f"  📨 Sent {ex.company} alert to your Telegram!")
                except Exception as e:
                    print(f"  ❌ Telegram dispatch failed: {e}")
            else:
                print("\n--- [WHATSAPP PREVIEW: NATIONAL EXAM] ---\n" + msg + "\n----------------------------------------")
    if new_exams_count == 0:
        print("  ⏭ All National Exams are already tracked in database.")

    # 4. Tier-1 Tech Radar (Google, Amazon, Microsoft, Goldman Sachs)
    print("\n💎 [4.5/5] Checking Tier-1 Tech Flagship Programs (Google, Amazon, MS, etc.)...")
    tier1_progs = get_tier1_programs()
    new_tier1_count = 0
    for prog in tier1_progs:
        if not is_already_sent(prog.job_id):
            new_tier1_count += 1
            print(f"  ✨ New Tier-1 Program: {prog.company} - {prog.role}")
            msg = format_job_alert_whatsapp(prog)
            if can_dispatch_telegram and not dry_run:
                try:
                    await send_alert_for_approval(
                        bot_token=TELEGRAM_BOT_TOKEN,
                        chat_id=TELEGRAM_ADMIN_CHAT_ID,
                        alert_id=prog.job_id,
                        title=f"{prog.company} - {prog.role}",
                        category="Tier-1 Tech Radar",
                        text=msg,
                        url=prog.apply_url
                    )
                    print(f"  📨 Sent {prog.company} Tier-1 alert to your Telegram!")
                except Exception as e:
                    print(f"  ❌ Telegram dispatch failed: {e}")
            else:
                print("\n--- [WHATSAPP PREVIEW: TIER-1 TECH] ---\n" + msg + "\n----------------------------------------")
    if new_tier1_count == 0:
        print("  ⏭ All Tier-1 programs are already tracked in database.")

    # 5. Summer 2027 Tech Internships (NVIDIA, Airbnb, Rivian, Workday/Greenhouse)
    print("\n🚀 [5/6] Checking Summer 2027 Open-Source Tech Radar...")
    github_jobs = fetch_github_college_jobs(limit=10)
    new_github_count = 0
    for g_job in github_jobs:
        if not is_already_sent(g_job.job_id):
            new_github_count += 1
            print(f"  ✨ New Summer 2027 Intern: {g_job.company} - {g_job.role}")
            msg = format_job_alert_whatsapp(g_job)
            if can_dispatch_telegram and not dry_run:
                try:
                    await send_alert_for_approval(
                        bot_token=TELEGRAM_BOT_TOKEN,
                        chat_id=TELEGRAM_ADMIN_CHAT_ID,
                        alert_id=g_job.job_id,
                        title=f"{g_job.company} - {g_job.role}",
                        category="Summer 2027 Intern",
                        text=msg,
                        url=g_job.apply_url
                    )
                except Exception as e:
                    print(f"  ❌ Telegram dispatch failed: {e}")
            else:
                print("\n--- [WHATSAPP PREVIEW: SUMMER 2027 INTERN] ---\n" + msg + "\n----------------------------------------")
            if new_github_count >= 3:
                break
    if new_github_count == 0:
        print("  ⏭ All GitHub summer internships already tracked.")

    # 6. Multi-Board Verified Tech Openings (LinkedIn, Internshala, Instahyre)
    print("\n💼 [6/6] Fetching Multi-Board Tech Openings (LinkedIn, Internshala, Instahyre)...")
    multi_jobs = fetch_all_multi_board_opportunities()
    new_multi_count = 0
    for job in multi_jobs:
        if not is_already_sent(job.job_id):
            new_multi_count += 1
            print(f"  ✨ New Opening: [{job.source}] {job.company} - {job.role}")
            msg = format_job_alert_whatsapp(job)
            if can_dispatch_telegram and not dry_run:
                try:
                    await send_alert_for_approval(
                        bot_token=TELEGRAM_BOT_TOKEN,
                        chat_id=TELEGRAM_ADMIN_CHAT_ID,
                        alert_id=job.job_id,
                        title=f"[{job.source}] {job.company} - {job.role}",
                        category=f"{job.source} Opening",
                        text=msg,
                        url=job.apply_url
                    )
                except Exception as e:
                    print(f"  ❌ Telegram dispatch failed: {e}")
            else:
                print("\n--- [WHATSAPP PREVIEW: MULTI-BOARD OPENING] ---\n" + msg + "\n------------------------------------")
            if new_multi_count >= 5:
                break
    if new_multi_count == 0:
        print("  ⏭ All multi-board tech jobs already tracked.")

    # 7. Hyderabad Hackathons & Tech Events (T-Hub, IIIT-H, Unstop)
    print("\n🏆 [7/7] Fetching Hyderabad Hackathons & Tech Events...")
    hyd_events = get_all_hyderabad_tech_events()
    new_hyd_count = 0
    for ev in hyd_events:
        if not is_already_sent(ev.job_id):
            new_hyd_count += 1
            print(f"  ✨ New Hyderabad Event: {ev.company} - {ev.role}")
            msg = format_job_alert_whatsapp(ev)
            if can_dispatch_telegram and not dry_run:
                try:
                    await send_alert_for_approval(
                        bot_token=TELEGRAM_BOT_TOKEN,
                        chat_id=TELEGRAM_ADMIN_CHAT_ID,
                        alert_id=ev.job_id,
                        title=f"{ev.company} - {ev.role}",
                        category="Hyd Hackathon",
                        text=msg,
                        url=ev.apply_url
                    )
                    mark_as_sent(ev.job_id, "dispatched", f"{ev.company} - {ev.role}", ev.apply_url)
                    print(f"  📨 Sent {ev.company} event to Telegram!")
                except Exception as e:
                    print(f"  ❌ Telegram dispatch failed: {e}")
            else:
                print("\n--- [WHATSAPP PREVIEW: HYDERABAD HACKATHON] ---\n" + msg + "\n----------------------------------------")
            if new_hyd_count >= 3:
                break
    if new_hyd_count == 0:
        print("  ⏭ All Hyderabad hackathons already tracked.")

    print("\n🎉 Pipeline Execution Completed Successfully!")

def run_pipeline(dry_run: bool = True):
    asyncio.run(run_pipeline_async(dry_run=dry_run))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="2027 Info Scraper and WhatsApp Dispatcher Engine")
    parser.add_argument("--live", action="store_true", help="Live mode (sends to Telegram for approval)")
    args = parser.parse_args()
    
    is_dry = not args.live
    print(f"Running pipeline in {'[DRY RUN - Local Preview]' if is_dry else '[LIVE - Dispatching to Telegram]'} mode...\n")
    run_pipeline(dry_run=is_dry)
