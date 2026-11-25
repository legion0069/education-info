import asyncio
import logging
from typing import Dict
from urllib.parse import quote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID
from database import mark_as_sent, is_already_sent

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# In-memory store for pending alerts: alert_id -> formatted WhatsApp text
PENDING_ALERTS: Dict[str, dict] = {}

def create_whatsapp_share_link(text: str) -> str:
    """Creates a native WhatsApp deep-link that opens WhatsApp with text pre-filled."""
    encoded_text = quote(text)
    return f"https://api.whatsapp.com/send?text={encoded_text}"

def create_linkedin_share_link(url: str) -> str:
    """Official LinkedIn share URL that reliably opens the Post Composer on both mobile & desktop."""
    return f"https://www.linkedin.com/sharing/share-offsite/?url={quote(url)}"

async def send_alert_for_approval(bot_token: str, chat_id: str, alert_id: str, title: str, category: str, text: str, url: str):
    """Sends a formatted alert to the Admin's Telegram with interactive Approval buttons."""
    from telegram import Bot
    bot = Bot(token=bot_token)
    
    # Store for when the admin clicks approve
    PENDING_ALERTS[alert_id] = {
        "title": title,
        "category": category,
        "text": text,
        "url": url
    }
    
    # One-click native share links
    wa_share_url = create_whatsapp_share_link(text)
    li_share_url = create_linkedin_share_link(url)
    
    keyboard = [
        [
            InlineKeyboardButton("🚀 1-Tap WhatsApp", url=wa_share_url),
            InlineKeyboardButton("💼 1-Tap LinkedIn", url=li_share_url)
        ],
        [
            InlineKeyboardButton("✅ Mark as Sent", callback_data=f"appr:{alert_id}"),
            InlineKeyboardButton("❌ Dismiss", callback_data=f"dism:{alert_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Telegram message preview
    preview_message = (
        f"🔔 *NEW OPPORTUNITY DETECTED FOR 2027 BATCH*\n"
        f"Category: `{category.upper()}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{text}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 *Admin Action Required:*"
    )
    
    await bot.send_message(
        chat_id=chat_id,
        text=preview_message,
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks on Telegram."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data or ":" not in data:
        return
        
    action, alert_id = data.split(":", 1)
    
    if action == "appr":
        alert_info = PENDING_ALERTS.get(alert_id, {})
        title = alert_info.get("title", "Opportunity")
        url = alert_info.get("url", "")
        category = alert_info.get("category", "alert")
        
        # Mark as sent in SQLite
        mark_as_sent(alert_id, category, title, url)
        
        await query.edit_message_text(
            text=f"{query.message.text}\n\n✅ *STATUS: APPROVED & RECORDED!*",
            reply_markup=None
        )
        logging.info(f"Alert {alert_id} approved and marked sent.")
        
    elif action == "dism":
        alert_info = PENDING_ALERTS.get(alert_id, {})
        title = alert_info.get("title", "Opportunity")
        url = alert_info.get("url", "")
        category = alert_info.get("category", "alert")
        
        # Mark as dismissed so it doesn't prompt again
        mark_as_sent(alert_id, f"dismissed_{category}", title, url)
        
        await query.edit_message_text(
            text=f"{query.message.text}\n\n❌ *STATUS: DISMISSED BY ADMIN.*",
            reply_markup=None
        )
        logging.info(f"Alert {alert_id} dismissed.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command to verify bot is running and check Chat ID."""
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Hello {user_name}!\n\n"
        f"I am your *2027 Placements & Internship Admin Bot*.\n"
        f"Your Chat ID is: `{chat_id}`\n\n"
        f"Whenever new TCS NQT drives, Deloitte NLA drives, Unstop internships, or LeetCode POTD are detected, "
        f"I will send them here with an instant approval button!"
    )

def run_bot():
    """Starts the bot listener."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is not configured in .env")
        return
        
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🤖 Telegram Admin Bot is listening for approvals...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
