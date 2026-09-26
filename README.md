import telebot, sqlite3, threading, time, os

TOKEN_EL_MASNA3 = os.environ.get("TOKEN") # هياخده من ريلواي اوتوماتيك
bot = telebot.TeleBot(TOKEN_EL_MASNA3)

db = sqlite3.connect('/data/masna3.db', check_same_thread=False) if os.path.exists('/data') else sqlite3.connect('masna3.db', check_same_thread=False)
db.execute('CREATE TABLE IF NOT EXISTS bots (user_id INTEGER, token TEXT, bot_username TEXT)')
db.commit()

def shaghal_el_bot(token):
    try:
        bot_gdeed = telebot.TeleBot(token)
        @bot_gdeed.message_handler(commands=['start'])
        def salam(m):
            bot_gdeed.send_message(m.chat.id, f"أهلا يا {m.from_user.first_name} ❤️\nأنا شغال من المصنع المصري 🇪🇬")
        @bot_gdeed.message_handler(func=lambda m: True)
        def rad(m):
            bot_gdeed.send_message(m.chat.id, f"استلمت: {m.text}")
        bot_gdeed.infinity_polling()
    except Exception as e:
        print(e)

@bot.message_handler(commands=['start','sna3_bot','botsy'])
def handle(m):
    if m.text == '/start':
        bot.send_message(m.chat.id, f"أهلا يا {m.from_user.first_name} في مصنع البوتات المصري 🇪🇬\nدوس /sna3_bot عشان تصنع بوت")
    elif m.text == '/sna3_bot':
        msg = bot.send_message(m.chat.id, "ابعتلي توكن البوت من @BotFather")
        bot.register_next_step_handler(msg, lambda x: save_token(x))
    elif m.text == '/botsy':
        rows = db.execute("SELECT bot_username FROM bots WHERE user_id=?", (m.from_user.id,)).fetchall()
        bot.send_message(m.chat.id, "\n".join([f"@{r[0]}" for r in rows]) if rows else "لسه معملتش بوتات")

def save_token(m):
    token = m.text.strip()
    try:
        b = telebot.TeleBot(token)
        me = b.get_me()
        db.execute("INSERT INTO bots VALUES (?,?,?)", (m.from_user.id, token, me.username))
        db.commit()
        threading.Thread(target=shaghal_el_bot, args=(token,), daemon=True).start()
        bot.send_message(m.chat.id, f"عاش! بوتك @ {me.username} اشتغل ✅")
    except:
        bot.send_message(m.chat.id, "التوكن بايظ، جرب تاني")

# شغل البوتات القديمة
for r in db.execute("SELECT token FROM bots").fetchall():
    threading.Thread(target=shaghal_el_bot, args=(r[0],), daemon=True).start()

print("المصنع جاهز")
bot.infinity_polling()
