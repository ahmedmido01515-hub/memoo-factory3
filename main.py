import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# --- جلب البيانات الحقيقية بأمان من المتغيرات البيئية للمنصة ---
API_ID = int(os.environ.get("API_ID", 1234567))                  
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")      
BOT_TOKEN = os.environ.get("TOKEN") # سيتم جلبه تلقائياً من إعدادات ريلواي لضمان الأمان
OWNER_USERNAME = "MernaQueen"        

DB_FILE = "factory_db.json"

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

app = Client("MemoFactory", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
running_bots = {}

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
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 قناة السورس", url="https://t.me")],
        [InlineKeyboardButton("👨‍💻 مطور المصنع", url=f"https://t.me{OWNER_USERNAME}")]
    ])
    await message.reply_text(welcome_msg, reply_markup=keyboard)

@app.on_message(filters.text & filters.private)
async def create_bot_handler(client: Client, message: Message):
    token = message.text.strip()
    user_id = message.from_user.id

    if ":" not in token or len(token) < 30:
        await message.reply_text("❌ **خطأ:** التوكن المرسل غير صحيح! تأكد من نسخه بالكامل من @BotFather.")
        return

    bots_db = load_bots()
    if token in bots_db or token in running_bots:
        await message.reply_text("⚠️ **تنبيه:** هذا البوت يعمل بالفعل على سيرفر المصنع ومفعل مسبقاً!")
        return

    await message.reply_text("⏳ **جاري فحص التوكن وتنصيب ملفات الحماية على السيرفر الخاص بك...**")

    try:
        child_bot = Client(f"memo_bot_{user_id}", api_id=API_ID, api_hash=API_HASH, bot_token=token)

        @child_bot.on_message(filters.group & (filters.regex(r"t\.me/") | filters.regex(r"@[a-zA-Z0-9_]+") | filters.regex(r"https?://")))
        async def link_protection(c: Client, msg: Message):
            try:
                member = await msg.chat.get_member(msg.from_user.id)
                if member.status in ["administrator", "creator"]:
                    return
                await msg.delete()
                await msg.chat.ban_member(msg.from_user.id)
            except Exception:
                pass

        @child_bot.on_message(filters.group & filters.forwarded)
        async def forward_protection(c: Client, msg: Message):
            try:
                member = await msg.chat.get_member(msg.from_user.id)
                if member.status in ["administrator", "creator"]:
                    return
                await msg.delete()
            except Exception:
                pass

        await child_bot.start()
        running_bots[token] = child_bot
        save_bot(token, user_id)

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

if __name__ == "__main__":
    print("🚀 سورس مصنع ميمو يعمل الآن بنجاح...")
    app.run()
