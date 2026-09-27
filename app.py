import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# --- 🛠️ بيانات مصنع بوتات حماية ميمو الحقيقية والمحدثة ---
API_ID = 1234567                     # 🔵 ضع هنا الـ API ID الخاص بك (أرقام فقط المستخرجة من my.telegram.org)
API_HASH = "your_api_hash_here"      # 🔵 ضع هنا الـ API HASH الخاص بك بين علامتي التنصيص
BOT_TOKEN = "8835297704:AAGIZ-VXLMSrPz-zLcQEMsoqh4WMhOenOmQ"  # ✅ تم تعيين توكن المصنع الحقيقي
OWNER_USERNAME = "MernaQueen"        # ✅ تم تعيين معرف المطور الحقيقي

# ملف محلي لتخزين توكنات البوتات مصنوعة لمنع ضياع البيانات عند ريستارت السيرفر
DB_FILE = "factory_db.json"

# إعداد وتثبيت قاعدة البيانات المصغرة
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_bots():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_bot(token, user_id):
    bots = load_bots()
    bots[token] = user_id
    with open(DB_FILE, "w") as f:
        json.dump(bots, f, indent=4)

# تشغيل كليّنت المصنع الأساسي
app = Client("MemoFactory", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
running_bots = {}

# 1. رسالة ترحيب البوت المصنع الأساسي (@memoo_factory_bot)
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    welcome_msg = (
        "🛡️ **أهلاً بك في مصنع بوتات حماية Memo مجاني!**\n\n"
        "الآن يمكنك إنشاء بوت حماية خاص بمجموعتك مجاناً وبسرعة.\n\n"
        "**الخطوات:**\n"
        "1️⃣ اذهب إلى @BotFather وقم بإنشاء بوت جديد.\n"
        "2️⃣ انسخ الـ **Token** الذي سيمنحه لك.\n"
        "3️⃣ أرسل التوكن هنا مباشرة ليتم تفعيل الحماية وتجهيز السيرفر لعملك."
    )
    # أزرار شفافة مدمجة (قناة السورس والدعم الفني للمطور)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 قناة السورس", url="https://t.me")],
        [InlineKeyboardButton("👨‍💻 مطور المصنع", url=f"https://t.me{OWNER_USERNAME}")]
    ])
    await message.reply_text(welcome_msg, reply_markup=keyboard)

# 2. استقبال توكن البوت وتشغيله وتطبيق حماية "سورس ميمو"
@app.on_message(filters.text & filters.private)
async def create_bot_handler(client: Client, message: Message):
    token = message.text.strip()
    user_id = message.from_user.id

    # التحقق المبدئي من صحة صيغة توكن تليجرام
    if ":" not in token or len(token) < 30:
        await message.reply_text("❌ **خطأ:** التوكن المرسل غير صحيح! تأكد من نسخه بالكامل من @BotFather.")
        return

    bots_db = load_bots()
    if token in bots_db or token in running_bots:
        await message.reply_text("⚠️ **تنبيه:** هذا البوت يعمل بالفعل على سيرفر المصنع ومفعل مسبقاً!")
        return

    await message.reply_text("⏳ **جاري فحص التوكن وتنصيب ملفات الحماية على السيرفر الخاص بك...**")

    try:
        # إنشاء نسخة فرعية مخصصة للبوت الجديد
        child_bot = Client(f"memo_bot_{user_id}", api_id=API_ID, api_hash=API_HASH, bot_token=token)

        # --- 🛡️ ميزات حماية سورس ميمو المدمجة تلقائياً داخل البوت المصنوع ---
        
        # أ. ميزة طرد الحسابات التي تنشر روابط تليجرام أو روابط إنترنت أو معرفات مزعجة
        @child_bot.on_message(filters.group & (filters.regex(r"t\.me/") | filters.regex(r"@[a-zA-Z0-9_]+") | filters.regex(r"https?://")))
        async def link_protection(c: Client, msg: Message):
            try:
                # التحقق أولاً من أن العضو المخالف ليس مشرفاً لتجنب طرد الإدارة
                member = await msg.chat.get_member(msg.from_user.id)
                if member.status in ["administrator", "creator"]:
                    return
                
                await msg.delete() # حذف رسالة الرابط فوراً
                await msg.chat.ban_member(msg.from_user.id) # طرد المخالف
            except Exception:
                pass

        # ب. ميزة منع التوجيه (Forward) لحماية المحتوى ومنع الإعلانات المنقولة
        @child_bot.on_message(filters.group & filters.forwarded)
        async def forward_protection(c: Client, msg: Message):
            try:
                member = await msg.chat.get_member(msg.from_user.id)
                if member.status in ["administrator", "creator"]:
                    return
                await msg.delete() # حذف المنشور الموجه تلقائياً
            except Exception:
                pass

        # تشغيل البوت وحفظ البيانات
        await child_bot.start()
        running_bots[token] = child_bot
        save_bot(token, user_id) # حفظ التوكن في قاعدة البيانات المحلية

        bot_info = await child_bot.get_me()
        success_text = (
            "✅ **تم إنشاء وتشغيل بوت الحماية الخاص بك بنجاح!**\n\n"
            f"🤖 **يوزر بوتك:** @{bot_info.username}\n"
            f"🆔 **معرف البوت:** `{bot_info.id}`\n\n"
            "**⚙️ خطوة التفعيل الأخيرة:**\n"
            "قم بإضافة البوت إلى مجموعتك، ثم قم برفعه **مشرفاً (Admin)** مع إعطائه كامل الصلاحيات ليعمل نظام حظر الروابط والتوجيه تلقائياً."
        )
        await message.reply_text(success_text)

    except Exception as e:
        await message.reply_text(f"❌ **فشل التثبيت:** تعذر تشغيل البوت عبر الخادم.\n**السبب:** `{str(e)}`")

# 3. دالة لتشغيل كافة البوتات المخزنة تلقائياً عند إعادة تشغيل السيرفر (تجنب توقف الخدمة)
async def auto_start_saved_bots():
    bots_db = load_bots()
    print(f"🔄 جاري إعادة تشغيل {len(bots_db)} بوت حماية من قاعدة البيانات...")
    for token, user_id in bots_db.items():
        try:
            child_bot = Client(f"memo_bot_{user_id}", api_id=API_ID, api_hash=API_HASH, bot_token=token)
            await child_bot.start()
            running_bots[token] = child_bot
        except Exception:
            print(f"❌ فشل تشغيل البوت صاحب التوكن: {token[:15]}...")

if __name__ == "__main__":
    print("🚀 سورس مصنع ميمو يعمل الآن بنجاح...")
    app.run()
