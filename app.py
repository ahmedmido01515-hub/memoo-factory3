import telebot, sqlite3, threading, time, os

# التوكن هيتاخد من Railway Variables - متكتبوش هنا
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    print("لازم تحط TOKEN في Variables بتاعة Railway")
    exit()

bot = telebot.TeleBot(TOKEN)

# لو فيه فولدر /data (الـ Volume) هنحفظ فيه الداتا بيز عشان متتمسحش
DB_PATH = '/data/masna3.db' if os.path.exists('/data') else 'masna3.db'
db = sqlite3.connect(DB_PATH, check_same_thread=False)
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
            bot_gdeed.send_message(m.chat.id, f"استلمت منك: {m.text}\nده رد من بوتك المصري.")

        print(f"شغلت البوت: {token[:15]}...")
        bot_gdeed.infinity_polling()
    except Exception as e:
        print(f"مشكلة في بوت {token[:15]}: {e}")

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, f"""أهلا يا {m.from_user.first_name} في مصنع البوتات المصري 🇪🇬🤖

دوس على:
/sna3_bot - عشان تصنع بوت جديد
/botsy - تشوف بوتاتك

الطريقة:
1- روح @BotFather
2- اعمل /newbot
3- خد التوكن وتعالى""")

@bot.message_handler(commands=['sna3_bot'])
def talap(m):
    msg = bot.send_message(m.chat.id, "ابعتلي توكن البوت اللي جبته من @BotFather")
    bot.register_next_step_handler(msg, save_token)

def save_token(m):
    token = m.text.strip()
    if ":" not in token:
        bot.send_message(m.chat.id, "التوكن شكله غلط، ابعت /sna3_bot تاني")
        return
    try:
        b = telebot.TeleBot(token)
        me = b.get_me()
        db.execute("INSERT INTO bots VALUES (?,?,?)", (m.from_user.id, token, me.username))
        db.commit()
        threading.Thread(target=shaghal_el_bot, args=(token,), daemon=True).start()
        bot.send_message(m.chat.id, f"عاش يا بطل! 🎉\nبوتك @{me.username} بقى شغال دلوقتي")
    except Exception as e:
        bot.send_message(m.chat.id, f"التوكن مش شغال: {e}")

@bot.message_handler(commands=['botsy'])
def botsy(m):
    rows = db.execute("SELECT bot_username FROM bots WHERE user_id=?", (m.from_user.id,)).fetchall()
    if not rows:
        bot.send_message(m.chat.id, "لسه معملتش بوتات، دوس /sna3_bot")
    else:
        msg = "بوتاتك:\n" + "\n".join([f"@{r[0]}" for r in rows])
        bot.send_message(m.chat.id, msg)

# شغل كل البوتات القديمة اول ما المصنع يقوم
for r in db.execute("SELECT token FROM bots").fetchall():
    threading.Thread(target=shaghal_el_bot, args=(r[0],), daemon=True).start()
    time.sleep(0.5)

print("المصنع المصري جاهز 🇪🇬")
bot.infinity_polling()
