import asyncio
import config
from telegram import Bot

async def test():
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    me = await bot.get_me()
    print(f"✅ Bot Authenticated: @{me.username} ({me.first_name})")
    
    msg = (
        "🎉 *Connection Successful!*\n\n"
        "Your *2027 Placements & Internship Radar Bot* is now connected to this chat.\n"
        "You will receive daily LeetCode POTD, Coding Contests, TCS NQT, Deloitte NLA, "
        "and Tech Internships right here with a 1-tap WhatsApp sharing button!"
    )
    await bot.send_message(
        chat_id=config.TELEGRAM_ADMIN_CHAT_ID,
        text=msg,
        parse_mode="Markdown"
    )
    print(f"🚀 Verification message sent to Chat ID: {config.TELEGRAM_ADMIN_CHAT_ID}")

if __name__ == "__main__":
    asyncio.run(test())
