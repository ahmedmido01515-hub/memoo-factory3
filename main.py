import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import Unauthorized, BackgroundIdInvalid 

### ==========================================

### ⚙️ CONFIGURATION

### ==========================================

API_ID = 1234567                 # ضع هنا الـ API ID الخاص بك
API_HASH = "your_api_hash_here"    # ضع هنا الـ API HASH الخاص بك
ADMIN_ID = 123456789              # آيدي حسابك الشخصي (مالك المصنع)
MAIN_BOT_TOKEN = "YOUR_MAIN_BOT_TOKEN_HERE" # توكن بوت المصنع الرئيسي 

### ==========================================

### 🗄️ DATABASE SETUP

### ==========================================

conn = sqlite3.connect("factory_database.db", check_same_thread=False)
cursor = conn.cursor() 

cursor.execute("""
CREATE TABLE IF NOT EXISTS bots (
token TEXT PRIMARY KEY,
owner_id INTEGER
)
""") 

cursor.execute("""
CREATE TABLE IF NOT EXISTS protected_groups (
bot_token TEXT,
group_id INTEGER,
welcome_msg TEXT DEFAULT 'Welcome to the group!',
lock_links INTEGER DEFAULT 0,
PRIMARY KEY (bot_token, group_id)
)
""")
conn.commit() 

### ==========================================

### 🤖 MAIN FACTORY CLIENT

### ==========================================

factory_app = Client("FactoryMainBot", api_id=API_ID, api_hash=API_HASH, bot_token=MAIN_BOT_TOKEN)
RUNNING_BOTS = {} 

def run_sub_bot(token):
if token in RUNNING_BOTS:
return
try:
sub_app = Client(f"bot_{token.split(':')}", api_id=API_ID, api_hash=API_HASH, bot_token=token) 

@sub_app.on_message(filters.command("start") & filters.private)
async def sub_start(client, message: Message):
    bot_user = await client.get_me()
    await message.reply_text(
        f"🤖 **أهلاً بك في بوت الحماية المتطور!**\n\nأنا بوت مخصص لحماية وتأمين المجموعات من السبام، الروابط، والتوجيه.\n\n**💡 طريقة التفعيل:**\n1️⃣ قم بإضافتي إلى مجموعتك.\n2️⃣ ارفعني رتبة **مشرف (Admin)** مع إعطائي كامل الصلاحيات لكي أعمل بشكل صحيح.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ أضف البوت إلى مجموعتك", url=f"https://t.me/{bot_user.username}?startgroup=true")]])
    )

@sub_app.on_message(filters.new_chat_members)
async def welcome_new_members(client, message: Message):
    bot_token = client.bot_token
    cursor.execute("SELECT welcome_msg FROM protected_groups WHERE bot_token=? AND group_id=?", (bot_token, message.chat.id))
    res = cursor.fetchone()
    welcome = res[0] if res else "Welcome to the group!"
    for member in message.new_chat_members:
        if not member.is_self:
            await message.reply_text(f"✨ مرحباً بك {member.mention} {welcome}")

@sub_app.on_message(filters.group & ~filters.service)
async def group_protection(client, message: Message):
    if not message.from_user:
        return
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status in ["administrator", "creator"]:
        if message.text == "قفل الروابط":
            cursor.execute("INSERT OR REPLACE INTO protected_groups (bot_token, group_id, lock_links) VALUES (?, ?, 1)", (client.bot_token, message.chat.id))
            conn.commit()
            await message.reply_text("🔒 **تم قفل الروابط بنجاح. سيتم حذف أي رابط يرسله الأعضاء.**")
        elif message.text == "فتح الروابط":
            cursor.execute("INSERT OR REPLACE INTO protected_groups (bot_token, group_id, lock_links) VALUES (?, ?, 0)", (client.bot_token, message.chat.id))
            conn.commit()
            await message.reply_text("🔓 **تم فتح الروابط في المجموعة.**")
        return
    cursor.execute("SELECT lock_links FROM protected_groups WHERE bot_token=? AND group_id=?", (client.bot_token, message.chat.id))
    res = cursor.fetchone()
    if res and res[0] == 1:
        if message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link", "mention"]:
                    try:
                        await message.delete()
                        await message.reply_text(f"⚠️ العضو {message.from_user.mention} ممنوع إرسال الروابط هنا!")
                    except:
                        pass
                    return

sub_app.start()
RUNNING_BOTS[token] = sub_app

except Exception as e:
print(f"Failed to start bot {token[:10]}: {e}")

def start_all_sub_bots():
cursor.execute("SELECT token FROM bots")
rows = cursor.fetchall()
for row in rows:
run_sub_bot(row) 

### ==========================================

### 🎮 MAIN FACTORY COMMANDS

### ==========================================

@factory_app.on_message(filters.command("start") & filters.private)
async def factory_start(client, message: Message):
await message.reply_text(
"👋 **مرحباً بك في مصنع بوتات حماية المجموعات المطور!**\n\nهنا يمكنك إنشاء وتجهيز بوت حماية كامل خاص بمجموعتك مجاناً وبكامل الحقوق.\n\n**⚙️ خطوات الصنع الهينة:**\n1️⃣ اذهب إلى البوت الرسمي @BotFather واصنع بوت جديد.\n2️⃣ قم بنسخ التوكن (Token) الذي يمنحه لك البوت.\n3️⃣ أرسل التوكن هنا مباشرة في الشات وسيتم تفعيل بوتك فوراً.",
reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻 مطور المصنع", user_id=ADMIN_ID)]])
) 

@factory_app.on_message(filters.private & ~filters.command(["start", "stats"]))
async def handle_token_creation(client, message: Message):
token = message.text.strip()
if ":" not in token or len(token) < 30:
await message.reply_text("❌ عذراً، هذا النص لا يبدو توكن بوت تليجرام صحيح. تأكد من نسخه بشكل صحيح من @BotFather")
return
cursor.execute("SELECT owner_id FROM bots WHERE token=?", (token,))
if cursor.fetchone():
await message.reply_text("⚠️ هذا البوت تم إنشاؤه مسبقاً في المصنع وهو يعمل الآن!")
return
progress = await message.reply_text("🔄 جاري التحقق من صحة التوكن وتشغيل الملفات...")
try:
run_sub_bot(token)
cursor.execute("INSERT INTO bots (token, owner_id) VALUES (?, ?)", (token, message.from_user.id))
conn.commit()
bot_me = await RUNNING_BOTS[token].get_me()
await progress.edit_text(f"✅ **تم تشغيل وتفعيل بوت الحماية الخاص بك بنجاح!**\n\n🤖 **اسم البوت:** {bot_me.first_name}\n🔗 **معرف البوت:** @{bot_me.username}\n\nاضغط على معرف بوتك، وأرسل /start وقم بإضافته لمجموعتك.")
except (Unauthorized, BackgroundIdInvalid):
await progress.edit_text("❌ تفشل العملية! التوكن الذي أرسلته خاطئ أو تم إلغاؤه من BotFather.")
except Exception as e:
await progress.edit_text(f"❌ حدث خطأ غير متوقع: {e}") 

@factory_app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def factory_stats(client, message: Message):
cursor.execute("SELECT COUNT(*) FROM bots")
await message.reply_text(f"📊 **إحصائيات مصنعك الحالية:**\n\n🤖 عدد البوتات المصنوعة والنشطة: {cursor.fetchone()}") 

if **name** == "**main**":
try:
start_all_sub_bots()
except Exception as err:
print(f"Error loading initial bots: {err}")
print("🚀 Factory Main Bot is starting...")
factory_app.run()
