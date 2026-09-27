import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import Unauthorized, BackgroundIdInvalid 

### ==========================================

### ⚙️ إعدادات المطور الأساسية (قم بتعديلها)

### ==========================================

API_ID = 1234567                 # ضع هنا الـ API ID الخاص بك من my.telegram.org
API_HASH = "your_api_hash_here"    # ضع هنا الـ API HASH الخاص بك
ADMIN_ID = 123456789              # آيدي حسابك الشخصي على تليجرام (مالك المصنع)
MAIN_BOT_TOKEN = "YOUR_MAIN_BOT_TOKEN_HERE" # توكن بوت المصنع الرئيسي من BotFather 

### ==========================================

### 🗄️ إعداد وتجهيز قاعدة البيانات

### ==========================================

conn = sqlite3.connect("factory_database.db", check_same_thread=False)
cursor = conn.cursor() 

### جدول لتخزين توكنات البوتات المصنوعة وأصحابها

cursor.execute("""
CREATE TABLE IF NOT EXISTS bots (
token TEXT PRIMARY KEY,
owner_id INTEGER
)
""") 

### جدول لتخزين إعدادات حماية المجموعات لكل بوت

cursor.execute("""
CREATE TABLE IF NOT EXISTS protected_groups (
bot_token TEXT,
group_id INTEGER,
welcome_msg TEXT DEFAULT 'أهلاً بك في المجموعة!',
lock_links INTEGER DEFAULT 0,
PRIMARY KEY (bot_token, group_id)
)
""")
conn.commit() 

### ==========================================

### 🤖 تشغيل العميل الرئيسي للمصنع

### ==========================================

factory_app = Client(
"FactoryMainBot",
api_id=API_ID,
api_hash=API_HASH,
bot_token=MAIN_BOT_TOKEN
) 

### مصفوفة في الذاكرة لتخزين البوتات النشطة برمجياً

RUNNING_BOTS = {} 

def run_sub_bot(token):
"""دالة ديناميكية لإنشاء وتشغيل بوت حماية فرعي فوراً"""
if token in RUNNING_BOTS:
return 

### إنشاء نسخة عميل مستقلة لكل توكن مصنوع

sub_app = Client(
f"bot_{token.split(':')}",
api_id=API_ID,
api_hash=API_HASH,
bot_token=token
) 

### --- [كود بوت الحماية الفرعي المصنوع] ---

@sub_app.on_message(filters.command("start") & filters.private)
async def sub_start(client, message: Message):
bot_user = await client.get_me()
await message.reply_text(
f"🤖 **أهلاً بك في بوت الحماية المتطور!**\n\n"
f"أنا بوت مخصص لحماية وتأمين المجموعات من السبام، الروابط، والتوجيه.\n\n"
f"**💡 طريقة التفعيل:**\n"
f"1️⃣ قم بإضافتي إلى مجموعتك.\n"
f"2️⃣ ارفعني رتبة **مشرف (Admin)** مع إعطائي كامل الصلاحيات لكي أعمل بشكل صحيح.",
reply_markup=InlineKeyboardMarkup([
[InlineKeyboardButton("➕ أضف البوت إلى مجموعتك", url=f"https://t.me/{bot_user.username}?startgroup=true")]
])
) 

@sub_app.on_message(filters.new_chat_members)
async def welcome_new_members(client, message: Message):
"""الترحيب التلقائي بالأعضاء الجدد"""
bot_token = client.bot_token
cursor.execute("SELECT welcome_msg FROM protected_groups WHERE bot_token=? AND group_id=?", (bot_token, message.chat.id))
res = cursor.fetchone()
welcome = res if res else "أهلاً بك في المجموعة!"
for member in message.new_chat_members:
if not member.is_self:
await message.reply_text(f"✨ مرحباً بك {member.mention} {welcome}") 

@sub_app.on_message(filters.group & ~filters.service)
async def group_protection(client, message: Message):
"""نظام فحص وحماية المجموعة وقفل الروابط"""
if not message.from_user:
return 

### التحقق من رتبة العضو (أدمن أم عضو عادي)

member = await client.get_chat_member(message.chat.id, message.from_user.id) 

if member.status in ["administrator", "creator"]: 

### أوامر التحكم للأدمنز داخل المجموعة

if message.text == "قفل الروابط":
cursor.execute("INSERT OR REPLACE INTO protected_groups (bot_token, group_id, lock_links) VALUES (?, ?, 1)", (client.bot_token, message.chat.id))
conn.commit()
await message.reply_text("🔒 **تم قفل الروابط بنجاح. سيتم حذف أي رابط يرسله الأعضاء.**")
return
elif message.text == "فتح الروابط":
cursor.execute("INSERT OR REPLACE INTO protected_groups (bot_token, group_id, lock_links) VALUES (?, ?, 0)", (client.bot_token, message.chat.id))
conn.commit()
await message.reply_text("🔓 **تم فتح الروابط في المجموعة.**")
return
return 

### تطبيق القوانين على الأعضاء العاديين

cursor.execute("SELECT lock_links FROM protected_groups WHERE bot_token=? AND group_id=?", (client.bot_token, message.chat.id))
res = cursor.fetchone()
if res and res == 1: 

### فحص إذا كانت الرسالة تحتوي على روابط أو معرفات قنوات

if message.entities:
for entity in message.entities:
if entity.type in ["url", "text_link", "mention"]:
try:
await message.delete()  # حذف الرابط فوراً
await message.reply_text(f"⚠️ العضو {message.from_user.mention} ممنوع إرسال الروابط هنا!")
except Exception:
pass
return 

# تشغيل البوت وحفظه في المصفوفة النشطة

sub_app.start()
RUNNING_BOTS[token] = sub_app

def start_all_sub_bots():
"""دالة لاستدعاء وتشغيل كل البوتات المخزنة في قاعدة البيانات عند إقلاع السيرفر"""
cursor.execute("SELECT token FROM bots")
rows = cursor.fetchall()
for row in rows:
token = row
try:
run_sub_bot(token)
except Exception as e:
print(f"⚠️ تعذر تشغيل التوكن المسترجع [{token[:12]}...]: {e}") 

### ==========================================

### 🎮 لوحة تحكم وأوامر المصنع الرئيسي

### ==========================================

@factory_app.on_message(filters.command("start") & filters.private)
async def factory_start(client, message: Message):
await message.reply_text(
"👋 **مرحباً بك في مصنع بوتات حماية المجموعات المطور!**\n\n"
"هنا يمكنك إنشاء وتجهيز بوت حماية كامل خاص بمجموعتك مجاناً وبكامل الحقوق.\n\n"
"**⚙️ خطوات الصنع الهينة:**\n"
"1️⃣ اذهب إلى البوت الرسمي @BotFather واصنع بوت جديد.\n"
"2️⃣ قم بنسخ التوكن (Token) الذي يمنحه لك البوت.\n"
"3️⃣ أرسل التوكن هنا مباشرة في الشات وسيتم تفعيل بوتك فوراً.",
reply_markup=InlineKeyboardMarkup([
[InlineKeyboardButton("👨‍💻 مطور المصنع", user_id=ADMIN_ID)]
])
) 

@factory_app.on_message(filters.private & ~filters.command(["start", "stats"]))
async def handle_token_creation(client, message: Message):
token = message.text.strip() 

### فحص أولي لتركيبة التوكن

if ":" not in token or len(token) < 30:
await message.reply_text("❌ عذراً، هذا النص لا يبدو توكن بوت تليجرام صحيح. تأكد من نسخه بشكل صحيح من @BotFather")
return 

### التحقق من عدم تكرار البوت

cursor.execute("SELECT owner_id FROM bots WHERE token=?", (token,))
exist = cursor.fetchone()
if exist:
await message.reply_text("⚠️ هذا البوت تم إنشاؤه مسبقاً في المصنع وهو يعمل الآن!")
return 

progress = await message.reply_text("🔄 جاري التحقق من صحة التوكن وتشغيل الملفات...") 

try: 

### تشغيل البوت ديناميكياً وحفظه بالقاعدة

run_sub_bot(token)
cursor.execute("INSERT INTO bots (token, owner_id) VALUES (?, ?)", (token, message.from_user.id))
conn.commit() 

# جلب يوزر البوت المصنوع لعرضه للمستخدم
target_bot = RUNNING_BOTS[token]
bot_me = await target_bot.get_me()

await progress.edit_text(
    f"✅ **تم تشغيل وتفعيل بوت الحماية الخاص بك بنجاح!**\n\n"
    f"🤖 **اسم البوت:** {bot_me.first_name}\n"
    f"🔗 **معرف البوت:** @{bot_me.username}\n\n"
    f"اضغط على معرف بوتك، وأرسل `/start` ثم قم بإضافته لمجموعتك ورفعه أدمن ليقوم بدوره في الحماية التلقائية."
)

except (Unauthorized, BackgroundIdInvalid):
await progress.edit_text("❌ تفشل العملية! التوكن الذي أرسلته خاطئ أو تم إلغاؤه من BotFather.")
except Exception as e:
await progress.edit_text(f"❌ حدث خطأ غير متوقع أثناء تهيئة السورس الداخلي: {e}")

@factory_app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def factory_stats(client, message: Message):
"""إحصائيات المصنع لمالك البوت فقط"""
cursor.execute("SELECT COUNT(*) FROM bots")
total_bots = cursor.fetchone()
await message.reply_text(f"📊 **إحصائيات مصنعك الحالية:**\n\n🤖 عدد البوتات المصنوعة والنشطة: {total_bots}") 

### ==========================================

### 🚀 إقلاع السيرفر والتشغيل المستمر

### ==========================================

if **name** == "**main**":
print("⚡ جاري استدعاء البوتات المصنوعة مسبقاً وتشغيلها...")
try:
start_all_sub_bots()
print("✅ تم تشغيل كافة البوتات الفرعية بنجاح.")
except Exception as err:
print(f"⚠️ خطأ أثناء تشغيل البوتات السابقة: {err}") 

print("🚀 جاري بدء تشغيل مصنع البوتات الرئيسي...")
factory_app.run()
