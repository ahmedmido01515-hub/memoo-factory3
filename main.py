import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import Unauthorized

API_ID = 1234567
API_HASH = "your_api_hash_here"
ADMIN_ID = 123456789
MAIN_BOT_TOKEN = "YOUR_MAIN_BOT_TOKEN_HERE"

conn = sqlite3.connect("factory_database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS bots (token TEXT PRIMARY KEY, owner_id INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS protected_groups (bot_token TEXT, group_id INTEGER, welcome_msg TEXT DEFAULT 'Welcome', lock_links INTEGER DEFAULT 0, PRIMARY KEY (bot_token, group_id))")
conn.commit()

factory_app = Client("FactoryMainBot", api_id=API_ID, api_hash=API_HASH, bot_token=MAIN_BOT_TOKEN)
RUNNING_BOTS = {}

def run_sub_bot(token):
    if token in RUNNING_BOTS:
        return
    try:
        # أخذ الجزء الأول من التوكن فقط لتسمية الجلسة لتجنب مشاكل الرموز
        session_name = f"bot_{token.split(':')[0]}"
        sub_app = Client(session_name, api_id=API_ID, api_hash=API_HASH, bot_token=token)
        
        @sub_app.on_message(filters.command("start") & filters.private)
        async def sub_start(client, message: Message):
            bot_user = await client.get_me()
            text = "🤖 أهلاً بك في بوت الحماية المطور!\n\nقم بإضافتي لمجموعتك وارفعني مشرفاً بصلاحيات كاملة لتفعيل الحماية."
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton("➕ إضافة البوت للمجموعة", url=f"https://t.me{bot_user.username}?startgroup=true")]])
            await message.reply_text(text, reply_markup=buttons)

        @sub_app.on_message(filters.new_chat_members)
        async def welcome_members(client, message: Message):
            bot_token = client.bot_token
            cursor.execute("SELECT welcome_msg FROM protected_groups WHERE bot_token=? AND group_id=?", (bot_token, message.chat.id))
            res = cursor.fetchone()
            welcome = res[0] if res else "أهلاً بك في المجموعة!"
            for member in message.new_chat_members:
                if not member.is_self:
                    await message.reply_text(f"✨ مرحباً بك {member.mention}\n{welcome}")

        @sub_app.on_message(filters.group & ~filters.service)
        async def group_protection(client, message: Message):
            if not message.from_user:
                return
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in ["administrator", "creator"]:
                if message.text == "قفل الروابط":
                    cursor.execute("INSERT OR REPLACE INTO protected_groups (bot_token, group_id, lock_links) VALUES (?, ?, 1)", (client.bot_token, message.chat.id))
                    conn.commit()
                    await message.reply_text("🔒 تم قفل الروابط بنجاح.")
                elif message.text == "فتح الروابط":
                    cursor.execute("INSERT OR REPLACE INTO protected_groups (bot_token, group_id, lock_links) VALUES (?, ?, 0)", (client.bot_token, message.chat.id))
                    conn.commit()
                    await message.reply_text("🔓 تم فتح الروابط.")
                return
            cursor.execute("SELECT lock_links FROM protected_groups WHERE bot_token=? AND group_id=?", (client.bot_token, message.chat.id))
            res = cursor.fetchone()
            if res and res[0] == 1:
                if message.entities:
                    for entity in message.entities:
                        if entity.type in ["url", "text_link", "mention"]:
                            try:
                                await message.delete()
                                await message.reply_text(f"⚠️ العضو {message.from_user.mention} ممنوع إرسال الروابط!")
                            except:
                                pass
                            return

        sub_app.start()
        RUNNING_BOTS[token] = sub_app
    except Exception as e:
        print(f"Error starting sub bot: {e}")

def start_all_sub_bots():
    cursor.execute("SELECT token FROM bots")
    rows = cursor.fetchall()
    for row in rows:
        run_sub_bot(row[0])

@factory_app.on_message(filters.command("start") & filters.private)
async def factory_start(client, message: Message):
    text = "👋 مرحباً بك في مصنع بوتات الحماية.\n\nارسـل توكن بوتك الآن لتفعيله فوراً."
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻 المطور", user_id=ADMIN_ID)]])
    await message.reply_text(text, reply_markup=buttons)

@factory_app.on_message(filters.private & ~filters.command(["start", "stats"]))
async def handle_token(client, message: Message):
    token = message.text.strip()
    if ":" not in token or len(token) < 30:
        await message.reply_text("❌ توكن غير صحيح.")
        return
    cursor.execute("SELECT owner_id FROM bots WHERE token=?", (token,))
    if cursor.fetchone():
        await message.reply_text("⚠️ البوت يعمل مسبقاً.")
        return
    progress = await message.reply_text("🔄 جاري التفعيل...")
    try:
        run_sub_bot(token)
        cursor.execute("INSERT INTO bots (token, owner_id) VALUES (?, ?)", (token, message.from_user.id))
        conn.commit()
        bot_me = await RUNNING_BOTS[token].get_me()
        await progress.edit_text(f"✅ تم تفعيل البوت بنجاح:\n🤖 @{bot_me.username}")
    except Unauthorized:
        await progress.edit_text("❌ التوكن خاطئ أو ملغي.")
    except Exception as e:
        await progress.edit_text(f"❌ خطأ في تشغيل البوت: {e}")

@factory_app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def factory_stats(client, message: Message):
    cursor.execute("SELECT COUNT(*) FROM bots")
    await message.reply_text(f"📊 عدد البوتات النشطة: {cursor.fetchone()[0]}")

if __name__ == "__main__":
    try:
        start_all_sub_bots()
    except Exception as err:
        print(f"Database error: {err}")
    print("🚀 Factory is starting...")
    factory_app.run()
