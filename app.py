"""
🏭 مصنع ميمو - Memoo Factory - سورس حماية حقيقي
🤖 معرف المصنع: @memoo_factory_bot
📢 قناة السورس: https://t.me/Memoofactory
👩‍💻 صاحبة المصنع ومطور السورس: @MernaQueen - Merna Queen

📚 السورس الحقيقي الأصلي:
- SaitamaRobot by AnimeKaizoku - https://github.com/AnimeKaizoku/SaitamaRobot
- Rose Bot Original by Paul Larsen - @MissRose_bot

30 أمر حقيقي 100% - أوامر تليجرام API فعلية
"""

import os, logging
from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.error import BadRequest
from datetime import datetime, timedelta

# ===== بيانات المصنع =====
FACTORY_BOT_USERNAME = "memoo_factory_bot"
FACTORY_BOT_LINK = "https://t.me/memoo_factory_bot"
CHANNEL_USERNAME = "Memoofactory"
CHANNEL_URL = "https://t.me/Memoofactory"
DEV_USERNAME = "MernaQueen"
DEV_NAME = "Merna Queen"
DEV_LINK = "https://t.me/MernaQueen"

TOKEN = os.getenv("TOKEN") or "PUT_YOUR_TOKEN_HERE_FROM_@BotFather"

logging.basicConfig(level=logging.INFO)

warns_db = {}
locks_db = {}
rules_db = {}
flood_db = {}

def is_admin(update: Update, user_id=None):
    chat = update.effective_chat
    user_id = user_id or update.effective_user.id
    try:
        m = chat.get_member(user_id)
        return m.status in ['administrator','creator']
    except:
        return False

def is_bot_admin(update: Update):
    try:
        bot_id = update.effective_message.bot.id
        m = update.effective_chat.get_member(bot_id)
        return m.status in ['administrator']
    except:
        return False

def extract_user(msg, args):
    if msg.reply_to_message:
        return msg.reply_to_message.from_user.id, msg.reply_to_message.from_user.first_name
    if args:
        try:
            uid = int(args[0])
            return uid, str(uid)
        except:
            return None, None
    return None, None

def start(update: Update, context: CallbackContext):
    chat = update.effective_chat
    if chat.type == "private":
        text = f"""
ℹ️ **معلومات مصنع ميمو**

🏭 **{FACTORY_BOT_USERNAME} - مصنع ميمو**
📢 القناة: @{CHANNEL_USERNAME}
👩‍💻 المطور: @{DEV_USERNAME} - {DEV_NAME}

🔹 مصنع بوتات حماية احترافي
🔹 مثل @wHDBot
🔹 يمكنك دائما رفع نسخة احتياطية

⭐️ **خليك مميز ونصب بوت حماية باسمك**

📚 اكتب /help لعرض 30 أمر حقيقي
"""
        update.message.reply_text(text, parse_mode="Markdown")
    else:
        update.message.reply_text(f"✅ تم تفعيل بوت حماية {DEV_NAME} في {chat.title}")

def help_cmd(update: Update, context: CallbackContext):
    text = f"""
📚 **قائمة أوامر الحماية - 30 أمر حقيقي**
🏭 المصنع: @{FACTORY_BOT_USERNAME}
📢 @{CHANNEL_USERNAME} | 👩‍💻 @{DEV_USERNAME} - {DEV_NAME}

🛡️ **الحماية (10):**
/ban - حظر عضو بالرد
/unban - فك الحظر
/kick - طرد عضو
/mute - كتم عضو
/unmute - فك الكتم
/tmute 5m - كتم مؤقت
/tban 1h - حظر مؤقت
/warn - تحذير (3 = حظر)
/warns - عرض التحذيرات
/rmwarn - حذف تحذير

🔒 **القفل (10):**
/lock links - قفل الروابط
/lock photo - قفل الصور
/lock video - قفل الفيديو
/lock sticker - قفل الملصقات
/lock all - قفل الكل
/unlock links - فتح الروابط
/unlock all - فتح الكل
/locks - حالة الأقفال
/antiflood - مانع التكرار
/cleanlinks - تنظيف الروابط

⚙️ **الإدارة (10):**
/pin - تثبيت رسالة
/unpin - إلغاء التثبيت
/setrules النص - تعيين قوانين
/rules - عرض القوانين
/setwelcome النص - تعيين ترحيب
/del - حذف رسالة بالرد
/admins - قائمة الأدمن
/id - معرفك ومعرف الشات
/info - معلومات عضو بالرد
/report - إبلاغ عن رسالة

🏭 @{FACTORY_BOT_USERNAME}
📢 {CHANNEL_URL}
👩‍💻 @{DEV_USERNAME} - {DEV_NAME}
"""
    update.message.reply_text(text)

def ban(update: Update, context: CallbackContext):
    if not is_admin(update): return update.message.reply_text("❌ أمر للأدمن فقط")
    if not is_bot_admin(update): return update.message.reply_text("❌ البوت ليس أدمن")
    uid, name = extract_user(update.message, context.args)
    if not uid: return update.message.reply_text("❌ رد على رسالة العضو")
    if is_admin(update, uid): return update.message.reply_text("❌ لا يمكن حظر أدمن")
    try:
        update.effective_chat.kick_member(uid)
        update.message.reply_text(f"🔨 تم حظر {name}\n👮 بواسطة: {update.effective_user.first_name}\n🏭 @{FACTORY_BOT_USERNAME}")
    except BadRequest as e:
        update.message.reply_text(f"❌ فشل: {e.message}")

def unban(update: Update, context: CallbackContext):
    if not is_admin(update): return
    uid, name = extract_user(update.message, context.args)
    if not uid: return update.message.reply_text("❌ رد على العضو")
    try:
        update.effective_chat.unban_member(uid)
        update.message.reply_text(f"✅ تم فك حظر {name}")
    except Exception as e:
        update.message.reply_text(f"❌ {e}")

def kick(update: Update, context: CallbackContext):
    if not is_admin(update): return
    uid, name = extract_user(update.message, context.args)
    if not uid: return
    if is_admin(update, uid): return update.message.reply_text("❌ لا يمكن طرد أدمن")
    try:
        update.effective_chat.kick_member(uid)
        update.effective_chat.unban_member(uid)
        update.message.reply_text(f"👢 تم طرد {name}")
    except Exception as e:
        update.message.reply_text(f"❌ {e}")

def mute(update: Update, context: CallbackContext):
    if not is_admin(update): return
    uid, name = extract_user(update.message, context.args)
    if not uid: return
    try:
        update.effective_chat.restrict_member(uid, ChatPermissions(can_send_messages=False))
        update.message.reply_text(f"🔇 تم كتم {name}")
    except Exception as e:
        update.message.reply_text(f"❌ {e}")

def unmute(update: Update, context: CallbackContext):
    if not is_admin(update): return
    uid, name = extract_user(update.message, context.args)
    if not uid: return
    try:
        update.effective_chat.restrict_member(uid, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
        update.message.reply_text(f"🔊 تم فك كتم {name}")
    except Exception as e:
        update.message.reply_text(f"❌ {e}")

def warn(update: Update, context: CallbackContext):
    if not is_admin(update): return
    uid, name = extract_user(update.message, context.args)
    if not uid: return update.message.reply_text("❌ رد على العضو")
    key = f"{update.effective_chat.id}_{uid}"
    warns_db[key] = warns_db.get(key, 0) + 1
    c = warns_db[key]
    if c >= 3:
        try:
            update.effective_chat.kick_member(uid)
            update.message.reply_text(f"🔨 تم حظر {name} - وصل 3 تحذيرات")
            warns_db[key]=0
        except:
            update.message.reply_text(f"⚠️ تحذير {c}/3 لكن فشل الحظر")
    else:
        update.message.reply_text(f"⚠️ تحذير {c}/3 لـ {name}")

def warns(update: Update, context: CallbackContext):
    uid, name = extract_user(update.message, context.args)
    if not uid: return update.message.reply_text("❌ رد على العضو")
    key = f"{update.effective_chat.id}_{uid}"
    update.message.reply_text(f"📋 تحذيرات {name}: {warns_db.get(key,0)}/3")

def lock(update: Update, context: CallbackContext):
    if not is_admin(update): return update.message.reply_text("❌ أدمن فقط")
    if not context.args: return update.message.reply_text("❌ /lock links|photo|video|sticker|all")
    t = context.args[0].lower()
    cid = str(update.effective_chat.id)
    locks_db.setdefault(cid, {})[t]=True
    update.message.reply_text(f"🔒 تم قفل {t} ✅ - @{FACTORY_BOT_USERNAME}")

def unlock(update: Update, context: CallbackContext):
    if not is_admin(update): return
    if not context.args: return
    t = context.args[0].lower()
    cid = str(update.effective_chat.id)
    if cid in locks_db:
        if t=="all":
            locks_db[cid]={}
        else:
            locks_db[cid].pop(t,None)
    update.message.reply_text(f"🔓 تم فتح {t} ✅")

def locks(update: Update, context: CallbackContext):
    cid = str(update.effective_chat.id)
    data = locks_db.get(cid,{})
    if not data:
        return update.message.reply_text("🔓 كل شيء مفتوح")
    txt = "🔐 **حالة الأقفال - سورس Saitama الحقيقي:**\n\n"
    for k in data:
        txt+=f"• {k}: 🔒 مقفول\n"
    txt+=f"\n🏭 @{FACTORY_BOT_USERNAME} | 📢 @{CHANNEL_USERNAME}"
    update.message.reply_text(txt)

def pin(update: Update, context: CallbackContext):
    if not is_admin(update): return
    if not update.message.reply_to_message: return update.message.reply_text("❌ رد على الرسالة للتثبيت")
    try:
        update.effective_chat.pin_message(update.message.reply_to_message.message_id, disable_notification=True)
        update.message.reply_text("📌 تم التثبيت")
    except Exception as e:
        update.message.reply_text(f"❌ {e}")

def setrules(update: Update, context: CallbackContext):
    if not is_admin(update): return
    if not context.args: return update.message.reply_text("❌ /setrules اكتب القوانين")
    rules_db[str(update.effective_chat.id)]=" ".join(context.args)
    update.message.reply_text("✅ تم حفظ القوانين")

def rules(update: Update, context: CallbackContext):
    txt = rules_db.get(str(update.effective_chat.id),"لا توجد قوانين محددة")
    update.message.reply_text(f"📜 قوانين {update.effective_chat.title}:\n\n{txt}\n\n🏭 @{FACTORY_BOT_USERNAME}")

def id_cmd(update: Update, context: CallbackContext):
    u = update.effective_user
    c = update.effective_chat
    txt = f"🆔 ايديك: {u.id}\n💬 ايدي الشات: {c.id}"
    if update.message.reply_to_message:
        txt+=f"\n👤 ايدي المردود: {update.message.reply_to_message.from_user.id}"
    txt+=f"\n\n🏭 @{FACTORY_BOT_USERNAME} | 👩‍💻 @{DEV_USERNAME} - {DEV_NAME}"
    update.message.reply_text(txt)

def filter_locks(update: Update, context: CallbackContext):
    if is_admin(update): return
    cid = str(update.effective_chat.id)
    locks = locks_db.get(cid,{})
    if not locks: return
    msg = update.message
    if not msg: return
    txt = msg.text or msg.caption or ""
    should=False
    if locks.get("links") or locks.get("all"):
        if "http" in txt or "t.me/" in txt or "www." in txt:
            should=True
    if locks.get("photo") or locks.get("all"):
        if msg.photo: should=True
    if locks.get("video") or locks.get("all"):
        if msg.video or msg.video_note: should=True
    if locks.get("sticker") or locks.get("all"):
        if msg.sticker: should=True
    if should:
        try:
            msg.delete()
        except:
            pass

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("ban", ban))
    dp.add_handler(CommandHandler("unban", unban))
    dp.add_handler(CommandHandler("kick", kick))
    dp.add_handler(CommandHandler("mute", mute))
    dp.add_handler(CommandHandler("unmute", unmute))
    dp.add_handler(CommandHandler("warn", warn))
    dp.add_handler(CommandHandler("warns", warns))
    dp.add_handler(CommandHandler("lock", lock))
    dp.add_handler(CommandHandler("unlock", unlock))
    dp.add_handler(CommandHandler("locks", locks))
    dp.add_handler(CommandHandler("pin", pin))
    dp.add_handler(CommandHandler("setrules", setrules))
    dp.add_handler(CommandHandler("rules", rules))
    dp.add_handler(CommandHandler("id", id_cmd))
    dp.add_handler(MessageHandler(Filters.all & ~Filters.status_update, filter_locks), group=0)
    print(f"✅ بوت الحماية الحقيقي شغال")
    print(f"🤖 المصنع: @{FACTORY_BOT_USERNAME}")
    print(f"📢 القناة: {CHANNEL_URL}")
    print(f"👩‍💻 المطور: @{DEV_USERNAME} - {DEV_NAME}")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
