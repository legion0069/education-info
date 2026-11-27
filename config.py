import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")
WHATSAPP_COMMUNITY_NAME = os.getenv("WHATSAPP_COMMUNITY_NAME", "2027 Tech & Placements")
WHATSAPP_INVITE_LINK = os.getenv("WHATSAPP_INVITE_LINK", "")
CRON_SECRET_TOKEN = os.getenv("CRON_SECRET_TOKEN", "radar2027secret")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_g6ONGKzC9aQr@ep-shiny-cake-bib04r36-pooler.c-5.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

def is_configured() -> bool:
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_CHAT_ID)
