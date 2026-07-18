import os
import asyncio
import json
from pathlib import Path
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ========== بياناتك ==========
BOT_TOKEN = "8704404185:AAGe_I8kcY4qtbpzVLxpTc2seLrPHHKLsvE"
API_ID = 38269251
API_HASH = "af81ddbd39ca658e08bf7c268d6651c7"
OWNER_ID = 5843701757

BASE_DIR = Path("/tmp/bot_sessions")
BASE_DIR.mkdir(exist_ok=True)

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "✅ Bot is running", 200

# ========== البوت ==========
async def main():
    bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

    @bot.on(events.NewMessage(pattern='/start'))
    async def start(event):
        await event.reply("🎯 البوت شغال")

    @bot.on(events.NewMessage)
    async def catch_all(event):
        print(f"📩 رسالة من {event.sender_id}: {event.text}")
        if event.sender_id == OWNER_ID:
            await event.reply(f"✅ استلمت أمرك: {event.text}")

    print("🚀 البوت شغال")
    await bot.run_until_disconnected()

def run_bot():
    asyncio.run(main())

# ========== تشغيل Flask ==========
if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
