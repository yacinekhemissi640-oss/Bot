import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# ========== بياناتك ==========
BOT_TOKEN = "8704404185:AAGe_I8kcY4qtbpzVLxpTc2seLrPHHKLsvE"
API_ID = 38269251
API_HASH = "af81ddbd39ca658e08bf7c268d6651c7"
OWNER_ID = 5843701757

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "✅ Bot is running", 200

# ========== تشغيل البوت ==========
async def start_bot():
    bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

    @bot.on(events.NewMessage(pattern='/start'))
    async def start(event):
        await event.reply("🎯 البوت شغال ✅")

    @bot.on(events.NewMessage)
    async def echo(event):
        print(f"📩 رسالة من {event.sender_id}: {event.text}")
        if event.sender_id == OWNER_ID:
            await event.reply(f"✅ استلمت: {event.text}")
        else:
            await event.reply("🌐 *Dz Quantum Net*\n🎁 خدمة تفعيل 2GB مجاني\n@Dz_off_bot")

    print("🚀 البوت شغال")
    await bot.run_until_disconnected()

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

# ========== تشغيل Flask ==========
if __name__ == "__main__":
    # تشغيل البوت في خلفية منفصلة
    thread = Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    
    # تشغيل Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
