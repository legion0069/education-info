import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")
WHATSAPP_COMMUNITY_NAME = os.getenv("WHATSAPP_COMMUNITY_NAME", "2027 Tech & Placements")
WHATSAPP_INVITE_LINK = os.getenv("WHATSAPP_INVITE_LINK", "")
CRON_SECRET_TOKEN = os.getenv("CRON_SECRET_TOKEN", "radar2027secret")

def is_configured() -> bool:
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_CHAT_ID)
