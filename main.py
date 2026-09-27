import os
import json
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant

# --- 🛠️ إعداد المتغيرات البيئية بأمان ---
API_ID = int(os.environ.get("API_ID", 1234567))                  
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")      
BOT_TOKEN = os.environ.get("TOKEN") 
OWNER_USERNAME = "MernaQueen"        
CHANNEL_LINK = "Memoofactory" # اسم معرف القناة بدون @

DB_FILE = "factory_db.json"
running_bots = {}

# --- إدارة قاعدة البيانات المصغرة ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"bots": {}, "users": []}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# تشغيل البوت المصنع الأساسي
app = Client("MemoFactoryPro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 📢 دالة التحقق من اشتراك القناة الإجباري ---
async def check_subscription(client: Client, user_id: int):
    try:
        await client.get_chat_member(CHANNEL_LINK, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return True # تجنب التوقف في حال وجود مشكلة بالصلاحيات

# ========================================================
# 1️⃣ الأوامر العامة وقائمة العميل (Client Menu)
# ========================================================

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    db = load_db()
    
    if user_id not in db["users"]:
        db["users"].append(user_id)
        save_db(db)

    # التحقق من الاشتراك الإجباري
    if not await check_subscription(client, user_id):
        buttons = [[InlineKeyboardButton("📢 اشترك في القناة أولاً", url=f"https://t.me{CHANNEL_LINK}")],
                   [InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_sub")]]
        await message.reply_text("⚠️ **عذراً عزيزي، يجب عليك الاشتراك في قناة السورس أولاً لاستخدام المصنع!**", reply_markup=InlineKeyboardMarkup(buttons))
        return

    is_owner = (message.from_user.username == OWNER_USERNAME)
    
    welcome_text = (
        f"🛡️ **أهلاً بك في مصنع بوتات حماية ميمو الاحترافي!**\n\n"
        f"يسعدنا خدمتك لتنصيب وتفعيل بوتات الحماية الخاصة بالمجموعات تلقائياً وبأعلى كفاءة.\n\n"
        f"💡 استخدم الأزرار بالأسفل للتحكم في خدمات المصنع."
    )
    
    buttons = [
        [InlineKeyboardButton("➕ صنع بوت حماية جديد", callback_data="create_bot")],
        [InlineKeyboardButton("❌ حذف أو إيقاف بوتك", callback_data="delete_bot")],
        [InlineKeyboardButton("📢 قناة السورس", url=f"https://t.me{CHANNEL_LINK}")]
    ]
    if is_owner:
        buttons.append([InlineKeyboardButton("⚙️ لوحة تحكم المطور", callback_data="owner_menu")])

    await message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(buttons))

# تفاعل الأزرار الشفافة للمصنع
@app.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    db = load_db()

    if data == "check_sub":
        if await check_subscription(client, user_id):
            await callback_query.answer("✅ تم التحقق بنجاح!", show_alert=True)
            await start_handler(client, callback_query.message)
        else:
            await callback_query.answer("❌ لم تشترك في القناة بعد!", show_alert=True)

    elif data == "create_bot":
        await callback_query.message.edit_text(
            "📥 **قم بإرسال توكن البوت الخاص بك الآن.**\n\n"
            "💡 للحصول على التوكن:\n"
            "1️⃣ اذهب إلى @BotFather واكتب `/newbot`.\n"
            "2️⃣ اختر اسماً ومعرفاً للبوت الخاص بك.\n"
            "3️⃣ انسخ الـ **Token** المرسل لك وقم بلصقه هنا مباشرة."
        )

    elif data == "delete_bot":
        user_bots = [token for token, uid in db["bots"].items() if uid == user_id]
        if not user_bots:
            await callback_query.answer("⚠️ ليس لديك أي بوتات مشغلة حالياً لتدميرها!", show_alert=True)
            return
        
        target_token = user_bots[0]
        if target_token in running_bots:
            try:
                await running_bots[target_token].stop()
                del running_bots[target_token]
            except Exception:
                pass
        
        if target_token in db["bots"]:
            del db["bots"][target_token]
        save_db(db)
        await callback_query.message.edit_text("✅ **تم إيقاف وحذف بوت الحماية الخاص بك بنجاح من خوادمنا.**")

    elif data == "owner_menu" and callback_query.from_user.username == OWNER_USERNAME:
        total_users = len(db["users"])
        total_bots = len(db["bots"])
        owner_text = (
            f"⚙️ **مرحباً بك في لوحة تحكم مطور المصنع ميمو:**\n\n"
            f"📊 **إحصائيات النظام الحالية:**\n"
            f"👤 عدد مستخدمي المصنع: `{total_users}`\n"
            f"🤖 عدد البوتات المصنوعة النشطة: `{total_bots}`"
        )
        buttons = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]]
        await callback_query.message.edit_text(owner_text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "main_menu":
        await start_handler(client, callback_query.message)

# ========================================================
# 2️⃣ تفعيل البوت واستقبال التوكن
# ========================================================

@app.on_message(filters.text & filters.private)
async def token_receiver(client: Client, message: Message):
    user_id = message.from_user.id
    token = message.text.strip()
    db = load_db()

    if ":" not in token or len(token) < 30:
        return

    if not await check_subscription(client, user_id):
        await message.reply_text("⚠️ يرجى الاشتراك في القناة أولاً لتفعيل الخدمة.")
        return

    if token in db["bots"] or token in running_bots:
        await message.reply_text("⚠️ هذا البوت منصب مسبقاً ويعمل على السيرفر!")
        return

    await message.reply_text("⏳ **جاري فحص التوكن البرمجي وتنصيب ميزات سورس ميمو المحترفة...**")

    try:
        clean_session_name = token.split(':')[0]
        child_bot = Client(f"child_{clean_session_name}", api_id=API_ID, api_hash=API_HASH, bot_token=token)

        # ========================================================
        # 3️⃣ أوامر وميزات البوت الفرعي المصنوع (Child Bot Logic)
        # ========================================================
        
        @child_bot.on_message(filters.command("start"))
        async def child_start(c: Client, m: Message):
            welcome = (
                f"🛡️ **مرحباً بك في بوت حماية المجموعات الاحترافي!**\n\n"
                f"⚙️ **وظيفتي:** حماية مجموعتك من التخريب، طرد ناشري الروابط، منع الإعلانات الموجهة والتوجيه تلقائياً.\n\n"
                f"💡 **طريقة التشغيل:** أضفني إلى مجموعتك وارفَعني بمقام **مشرف (Admin)** بكامل الصلاحيات."
            )
            buttons = [[InlineKeyboardButton("⚙️ قائمة الأوامر والإعدادات", callback_data="child_help")]]
            await m.reply_text(welcome, reply_markup=InlineKeyboardMarkup(buttons))

        @child_bot.on_callback_query()
        async def child_callback(c: Client, cb: CallbackQuery):
            if cb.data == "child_help":
                help_text = (
                    "⚙️ **قائمة أوامر الحماية التلقائية المفعّلة:**\n\n"
                    "1️⃣ **منع الروابط:** يتم حذف أي رابط إنترنت أو تليجرام مع طرد الحساب فوراُ.\n"
                    "2️⃣ **منع التوجيه:** يتم تنظيف وتصفية الإعلانات المنقولة من قنوات أخرى تلقائياً.\n"
                    "3️⃣ **تصفية المعرفات:** يتم كشف ومنع الترويج لمعرفات `@` داخل المجموعة.\n\n"
                    "⚠️ البوت يعمل بصمت وتلقائية بمجرد رفعه مشرفاً."
                )
                await cb.message.edit_text(help_text)

        @child_bot.on_message(filters.group & (filters.regex(r"t\.me/") | filters.regex(r"@[a-zA-Z0-9_]+") | filters.regex(r"https?://")))
        async def link_protection(c: Client, m: Message):
            try:
                member = await m.chat.get_member(m.from_user.id)
                if member.status in ["administrator", "creator"]:
                    return
                await m.delete()
                await m.chat.ban_member(m.from_user.id)
            except Exception:
                pass

        @child_bot.on_message(filters.group & filters.forwarded)
        async def forward_protection(c: Client, m: Message):
            try:
                member = await m.chat.get_member(m.from_user.id)
                if member.status in ["administrator", "creator"]:
                    return
                await m.delete()
            except Exception:
                pass

        await child_bot.start()
        running_bots[token] = child_bot
        db["bots"][token] = user_id
        save_db(db)

        bot_info = await child_bot.get_me()
        await message.reply_text(
            f"✅ **تم تنصيب وتفعيل بوت الحماية الاحترافي بنجاح!**\n\n"
            f"🤖 **يوزر البوت المصنوع:** @{bot_info.username}\n"
            f"🆔 **معرف الحماية:** `{bot_info.id}`\n\n"
            f"✨ البوت الآن جاهز للعمل ولديه قائمة ترحيب مخصصة وأمر `/start` بمجرد إضافته للمجموعات."
        )

    except Exception as e:
        await message.reply_text(f"❌ **فشل التفعيل:** تعذر تشغيل البوت.\n**السبب:** `{str(e)}`")

if __name__ == "__main__":
    print("🚀 سورس مصنع ميمو المحترف يعمل الآن...")
    app.run()
