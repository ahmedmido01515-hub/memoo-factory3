import telebot
import threading
import requests
import json
import os

# يقرأ التوكن من إعدادات Render
FACTORY_BOT_TOKEN = os.environ.get("FACTORY_TOKEN")
    # fallback للموبايل
    if os.path.exists("factory_token.txt"):
        with open("factory_token.txt","r") as f:
            FACTORY_BOT_TOKEN = f.read().strip()

print("🔥 مصنع Memo شغال 24 ساعة")

try:
    r = requests.get(f"https://api.telegram.org/bot{FACTORY_BOT_TOKEN}/getMe", timeout=10).json()
    if not r.get("ok"):
        print("❌ التوكن غلط!")
        exit()
    print(f"✅ المصنع شغال باسم: @{r['result']['username']}")
except Exception as e:
    print(f"❌ خطأ: {e}")
    exit()

factory_bot = telebot.TeleBot(FACTORY_BOT_TOKEN)
BOTS_FILE = "my_bots.json"

def load_bots():
    if os.path.exists(BOTS_FILE):
        try:
            with open(BOTS_FILE,"r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_bots(bots):
    with open(BOTS_FILE,"w") as f:
        json.dump(bots,f)

running_bots = {}

def run_protection_bot(token):
    try:
        bot = telebot.TeleBot(token)
        @bot.message_handler(content_types=['new_chat_members'])
        def protect(message):
            for member in message.new_chat_members:
                if member.is_bot:
                    try:
                        bot.kick_chat_member(message.chat.id, member.id)
                        bot.send_message(message.chat.id, f"تم طرد البوت {member.first_name} 🔒")
                    except: pass
        @bot.message_handler(func=lambda m: m.text and ("t.me" in m.text.lower() or "http" in m.text.lower()))
        def delete_links(message):
            try: bot.delete_message(message.chat.id, message.message_id)
            except: pass
        @bot.message_handler(commands=['start'])
        def start_user_bot(message):
            bot.reply_to(message, f"بوت الحماية شغال ✅\n@{bot.get_me().username}")
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print(f"Bot stopped: {e}")

def start_bot_thread(token):
    if token in running_bots:
        return False
    t = threading.Thread(target=run_protection_bot, args=(token,), daemon=True)
    t.start()
    running_bots[token]=t
    return True

@factory_bot.message_handler(commands=['start'])
def factory_start(message):
    factory_bot.send_message(message.chat.id, "🔥 اهلا بيك في مصنع Memo 🔥\n\nابعت توكن البوت اللي عايز تشغله حماية بس\nمن غير يوزر\n\nمثال:\n`123456:AAH-xxxx`\n\n/my_bots - لعرض بوتاتك", parse_mode="Markdown")

@factory_bot.message_handler(func=lambda m: ":" in m.text and len(m.text) > 35)
def handle_token(message):
    token = message.text.strip()
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10).json()
        if not r.get("ok"):
            factory_bot.reply_to(message, "❌ التوكن غلط")
            return
        username = r["result"]["username"]
        bots = load_bots()
        bots[token]=username
        save_bots(bots)
        if start_bot_thread(token):
            factory_bot.reply_to(message, f"✅ تم تشغيل البوت\n@{username}")
        else:
            factory_bot.reply_to(message, f"⚠️ البوت @{username} شغال اصلا")
    except Exception as e:
        factory_bot.reply_to(message, f"خطأ: {e}")

@factory_bot.message_handler(commands=['my_bots'])
def my_bots_list(message):
    bots = load_bots()
    if not bots:
        factory_bot.send_message(message.chat.id, "لسه معندكش بوتات")
        return
    text="🤖 بوتاتك:\n\n"
    for token, username in bots.items():
        text+=f"• @{username}\n"
    factory_bot.send_message(message.chat.id, text)

print("Memo Factory Online! شغال 24 ساعة")
old_bots=load_bots()
for token in old_bots:
    start_bot_thread(token)

factory_bot.infinity_polling(none_stop=True)
