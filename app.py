import json, os, threading, time, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

try:
    import yt_dlp
    YTDLP = True
except:
    YTDLP = False

try:
    import requests
    REQ = True
except:
    REQ = False

FACTORY_TOKEN = os.getenv("TOKEN") or os.getenv("FACTORY_TOKEN") or "8835297704:AAHwG3vBZEMly31PH-WqBFLUXhebU_LMUEA"
DATA_FILE = "bots_pro.json"
PREMIUM_FILE = "premium_users.json"

CHANNEL = "Memoofactory"
CHANNEL_URL = "https://t.me/Memoofactory"
DEV_USERNAME = "mernaqueen"
ADMIN_USERNAMES = ["mernaqueen", "MernaQueen", "MERNAQUEEN"]
ADMIN_IDS = []

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Memo Factory VIP - Auto BotFather - Subscriptions Active")
    def log_message(self, *a):
        pass

def start_web():
    port = int(os.getenv("PORT", 10000))
    try:
        HTTPServer(("0.0.0.0", port), Handler).serve_forever()
    except:
        pass

threading.Thread(target=start_web, daemon=True).start()

def call(token, method, data=None):
    try:
        url = f"https://api.telegram.org/bot{token}/{method}"
        payload = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=payload, headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def load_bots():
    if os.path.exists(DATA_FILE):
        try:
            return json.load(open(DATA_FILE, "r", encoding="utf-8"))
        except:
            return {}
    return {}

def save_bots(d):
    json.dump(d, open(DATA_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def load_premium():
    if os.path.exists(PREMIUM_FILE):
        try:
            return json.load(open(PREMIUM_FILE, "r", encoding="utf-8"))
        except:
            return {}
    return {}

def save_premium(d):
    json.dump(d, open(PREMIUM_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def is_premium_active(user_id):
    premium = load_premium()
    info = premium.get(str(user_id))
    if not info:
        for uid, data in premium.items():
            if str(data.get("user_id")) == str(user_id):
                info = data
                break
    if not info:
        return False, None
    expire = info.get("expire", 0)
    if expire > time.time():
        return True, info
    else:
        return False, info

def get_user_bots(all_bots, user_id):
    result = {}
    for username, info in all_bots.items():
        if str(info.get("owner_id")) == str(user_id):
            result[username] = info
    return result

def count_user_type(all_bots, user_id, btype):
    c = 0
    for info in all_bots.values():
        if str(info.get("owner_id")) == str(user_id) and info.get("type") == btype:
            c += 1
    return c

def is_admin_user(from_user):
    username = from_user.get("username", "")
    uid = from_user.get("id", 0)
    if username in ADMIN_USERNAMES:
        return True
    if str(uid) in ADMIN_IDS or uid in ADMIN_IDS:
        return True
    return False

def is_admin(token, chat_id, user_id):
    try:
        r = call(token, "getChatMember", {"chat_id": chat_id, "user_id": user_id})
        return r.get("result", {}).get("status") in ["administrator", "creator"]
    except:
        return False

def clean_cmd(text):
    if not text:
        return ""
    t = text.strip().split()[0]
    if "@" in t:
        t = t.split("@")[0]
    return t.lower()

def dl_tiktok(url):
    try:
        if REQ:
            r = requests.post("https://www.tikwm.com/api/", data={"url": url}, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
            j = r.json()
            if j.get("code")==0:
                d=j.get("data",{})
                return {"ok":True,"url":d.get("play") or d.get("hdplay"),"title":d.get("title","TikTok")}
    except:
        pass
    return {"ok":False}

def dl_yt(url):
    try:
        if YTDLP:
            opts={'quiet':True,'no_warnings':True,'noplaylist':True,'format':'best[ext=mp4]/best'}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info=ydl.extract_info(url,download=False)
                return {"ok":True,"url":info.get("url"),"title":info.get("title","Video")}
    except:
        pass
    return {"ok":False}

def setup_botfather_auto(token, btype, username):
    try:
        if btype == "protection":
            short = "🛡️ بوت حماية VIP - سورس ميمو | @Memoofactory"
            long_desc = f"✨ بوت الحماية المميز - سورس ميمو\n\n🤖 @{username}\n🛡️ حماية احترافية + مميزات VIP\n📢 @{CHANNEL}\n👨‍💻 @{DEV_USERNAME}\n\n⭐️ خليك مميز ونصب بوت حماية باسمك\n🔹 أوامر مقسمة 4 أقسام واضحة\n🔹 طرد/حظر/كتم بالرد - بدون مشاكل\n\n💎 مميزات VIP: نسخ احتياطي، إحصائيات، دعم 24/7"
            call(token, "setMyShortDescription", {"short_description": short})
            call(token, "setMyDescription", {"description": long_desc})
            cmds=[
                {"command":"start","description":"✨ بداية البوت VIP"},
                {"command":"help","description":"📚 الأقسام المقسمة (4 أقسام)"},
                {"command":"ban","description":"[حماية] 🔨 حظر بالرد"},
                {"command":"unban","description":"[حماية] ✅ فك الحظر"},
                {"command":"kick","description":"[حماية] 👢 طرد بالرد"},
                {"command":"mute","description":"[حماية] 🔇 كتم بالرد"},
                {"command":"unmute","description":"[حماية] 🔊 فك الكتم"},
                {"command":"warn","description":"[حماية] ⚠️ تحذير"},
                {"command":"warns","description":"[حماية] 📋 تحذيرات"},
                {"command":"lock","description":"[قفل] 🔒 قفل محتوى"},
                {"command":"unlock","description":"[قفل] 🔓 فتح"},
                {"command":"locks","description":"[قفل] 🔐 حالة الأقفال"},
                {"command":"pin","description":"[إدارة] 📌 تثبيت"},
                {"command":"unpin","description":"[إدارة] 📍 إلغاء تثبيت"},
                {"command":"setrules","description":"[إدارة] 📜 تعيين قوانين"},
                {"command":"setwelcome","description":"[إدارة] 👋 تعيين ترحيب"},
                {"command":"rules","description":"[معلومات] 📜 القوانين"},
                {"command":"id","description":"[معلومات] 🆔 الايدي"},
                {"command":"settings","description":"[معلومات] ⚙️ الإعدادات"},
            ]
        else:
            short = "📥 بوت تحميل VIP - سورس ميمو | @Memoofactory"
            long_desc = f"✨ بوت التحميل المميز - سورس ميمو\n\n🤖 @{username}\n📥 تيك توك/يوتيوب/انستا/فيسبوك/تويتر\n📢 @{CHANNEL}\n👨‍💻 @{DEV_USERNAME}"
            call(token, "setMyShortDescription", {"short_description": short})
            call(token, "setMyDescription", {"description": long_desc})
            cmds=[
                {"command":"start","description":"✨ بداية التحميل VIP"},
                {"command":"help","description":"📚 طريقة التحميل"},
                {"command":"download","description":"[تحميل] 📥 تحميل رابط"},
                {"command":"tiktok","description":"[تيك توك] 🎵 بدون علامة"},
                {"command":"youtube","description":"[يوتيوب] ▶️ تحميل"},
                {"command":"instagram","description":"[انستا] 📸 ريلز"},
                {"command":"facebook","description":"[فيسبوك] 🔵 فيديو"},
                {"command":"twitter","description":"[تويتر] 🐦 X"},
                {"command":"id","description":"🆔 ايديك"},
            ]
        call(token, "setMyCommands", {"commands": cmds})
        call(token, "setMyCommands", {"commands": cmds, "scope": {"type": "all_private_chats"}})
        call(token, "setMyCommands", {"commands": cmds, "scope": {"type": "all_group_chats"}})
        print(f"✅ BotFather Auto Linked @{username} {btype}")
        return True
    except Exception as e:
        print(f"setup error {e}")
        return False

def run_protection(token):
    me = call(token, "getMe")
    username = me.get("result",{}).get("username","") if me.get("ok") else ""
    setup_botfather_auto(token, "protection", username)
    offset=0
    locks={}
    warns={}
    welcome_texts={}
    rules_texts={}
    print(f"Protection VIP @{username} started")
    while True:
        try:
            res=call(token,"getUpdates",{"offset":offset,"timeout":25})
            for upd in res.get("result",[]):
                offset=upd["update_id"]+1
                if "callback_query" in upd:
                    cq=upd["callback_query"]
                    chat_id=cq["message"]["chat"]["id"]
                    data=cq["data"]
                    mid=cq["message"]["message_id"]
                    call(token,"answerCallbackQuery",{"callback_query_id":cq["id"]})
                    if data=="help_main":
                        kb={"inline_keyboard":[
                            [{"text":"🛡️ الحماية","callback_data":"sec_prot"},{"text":"🔒 القفل","callback_data":"sec_lock"}],
                            [{"text":"ℹ️ المعلومات","callback_data":"sec_info"},{"text":"⚙️ الإدارة","callback_data":"sec_admin"}],
                            [{"text":"📜 القوانين","callback_data":"show_rules"},{"text":"👋 الترحيب","callback_data":"show_welcome"}],
                            [{"text":"🔙 رجوع","callback_data":"back_start"}]
                        ]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":"📚 **أقسام أوامر الحماية VIP**","reply_markup":kb,"parse_mode":"Markdown"})
                    elif data=="sec_prot":
                        txt="🛡️ **قسم الحماية**\n\n• /ban - حظر بالرد\n• /unban - فك الحظر\n• /kick - طرد\n• /mute - كتم\n• /unmute - فك الكتم\n• /warn - تحذير\n• /warns - تحذيرات\n\n✅ شغال 100%"
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb})
                    elif data=="sec_lock":
                        txt="🔒 **قسم القفل**\n\n• /lock links - قفل الروابط\n• /lock photos - قفل الصور\n• /lock videos - قفل الفيديو\n• /lock all - قفل الكل\n• /unlock links - فتح\n• /locks - حالة الأقفال"
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb})
                    elif data=="sec_info":
                        txt="ℹ️ **المعلومات**\n\n• /id - الايدي\n• /rules - القوانين"
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb})
                    elif data=="sec_admin":
                        txt="⚙️ **الإدارة**\n\n• /pin - تثبيت بالرد\n• /unpin - إلغاء\n• /setrules النص - تعيين قوانين"
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb})
                    elif data=="show_rules":
                        rules=rules_texts.get(str(chat_id),"لا توجد قوانين")
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":f"📜 القوانين\n\n{rules}","reply_markup":kb})
                    elif data=="show_welcome":
                        wel=welcome_texts.get(str(chat_id),"أهلا وسهلا")
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":f"👋 الترحيب\n\n{wel}","reply_markup":kb})
                    elif data=="back_start":
                        kb={"inline_keyboard":[
                            [{"text":"➕ أضفني لمجموعتك","url":f"https://t.me/{username}?startgroup=new"}],
                            [{"text":"📚 الأقسام","callback_data":"help_main"}],
                            [{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]
                        ]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":f"✨ **بوت الحماية VIP**\n\n@{username}","reply_markup":kb})
                    continue
                msg=upd.get("message",{})
                chat=msg.get("chat",{})
                chat_id=chat.get("id")
                raw=msg.get("text","") or msg.get("caption","")
                text=clean_cmd(raw)
                from_id=msg.get("from",{}).get("id")
                reply=msg.get("reply_to_message")
                if not chat_id:
                    continue
                if chat.get("type")!="private":
                    cfg=locks.get(str(chat_id),{})
                    if from_id and not is_admin(token,chat_id,from_id):
                        should=False
                        if cfg.get("links") and ("http" in raw or "t.me/" in raw or "www." in raw):
                            should=True
                        if cfg.get("photos") and msg.get("photo"):
                            should=True
                        if cfg.get("videos") and (msg.get("video") or msg.get("video_note")):
                            should=True
                        if cfg.get("stickers") and msg.get("sticker"):
                            should=True
                        if should:
                            try:
                                call(token,"deleteMessage",{"chat_id":chat_id,"message_id":msg.get("message_id")})
                            except:
                                pass
                            continue
                if text=="/start":
                    kb={"inline_keyboard":[[{"text":"➕ أضفني لمجموعتك","url":f"https://t.me/{username}?startgroup=new"}],[{"text":"📚 الأقسام المقسمة","callback_data":"help_main"}],[{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]]}
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"✨ **بوت الحماية VIP**\n\n@{username}\n🛡️ أوامر مقسمة - ربط اوتوماتيك","reply_markup":kb,"parse_mode":"Markdown"})
                if text=="/help":
                    kb={"inline_keyboard":[[{"text":"🛡️ الحماية","callback_data":"sec_prot"},{"text":"🔒 القفل","callback_data":"sec_lock"}]]}
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"📚 **أقسام الأوامر**","reply_markup":kb})
                if text in ["تفعيل","/activate"]:
                    if chat.get("type")=="private":
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"أضفني مجموعة واكتب تفعيل"})
                    else:
                        if not is_admin(token,chat_id,from_id):
                            call(token,"sendMessage",{"chat_id":chat_id,"text":"❌ أدمن فقط"})
                        else:
                            call(token,"sendMessage",{"chat_id":chat_id,"text":f"✅ تم تفعيل {chat.get('title','')}"})
                if text=="/id":
                    txt=f"🆔 ايديك: `{from_id}`\n💬 ايدي الشات: `{chat_id}`"
                    if reply:
                        txt+=f"\n👤 المردود: `{reply['from']['id']}`"
                    call(token,"sendMessage",{"chat_id":chat_id,"text":txt,"parse_mode":"Markdown"})
                if text=="/rules":
                    rules=rules_texts.get(str(chat_id),"لا توجد قوانين")
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"📜 القوانين\n\n{rules}"})
                if raw.startswith("/setrules "):
                    if not is_admin(token,chat_id,from_id):
                        continue
                    rules_texts[str(chat_id)]=raw.replace("/setrules ","").strip()
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"✅ تم حفظ القوانين"})
                if raw.startswith("/setwelcome "):
                    if not is_admin(token,chat_id,from_id):
                        continue
                    welcome_texts[str(chat_id)]=raw.replace("/setwelcome ","").strip()
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"✅ تم حفظ الترحيب"})
                if text=="/locks":
                    cfg=locks.get(str(chat_id),{})
                    txt=f"🔐 الأقفال\n\nروابط: {'🔒' if cfg.get('links') else '🔓'}\nصور: {'🔒' if cfg.get('photos') else '🔓'}"
                    call(token,"sendMessage",{"chat_id":chat_id,"text":txt})
                if text in ["/kick","طرد"] and reply:
                    if not is_admin(token,chat_id,from_id):
                        continue
                    if is_admin(token,chat_id,reply["from"]["id"]):
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"❌ لا يمكن طرد أدمن"})
                        continue
                    call(token,"banChatMember",{"chat_id":chat_id,"user_id":reply["from"]["id"]})
                    call(token,"unbanChatMember",{"chat_id":chat_id,"user_id":reply["from"]["id"]})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"👢 طرد {reply['from'].get('first_name','')}"})
                if text in ["/ban","حظر"] and reply:
                    if not is_admin(token,chat_id,from_id):
                        continue
                    call(token,"banChatMember",{"chat_id":chat_id,"user_id":reply["from"]["id"]})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"🔨 حظر {reply['from'].get('first_name','')}"})
                if text in ["/unban","فك الحظر"] and reply:
                    if not is_admin(token,chat_id,from_id):
                        continue
                    call(token,"unbanChatMember",{"chat_id":chat_id,"user_id":reply["from"]["id"]})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"✅ فك حظر {reply['from'].get('first_name','')}"})
                if text in ["/mute","كتم"] and reply:
                    if not is_admin(token,chat_id,from_id):
                        continue
                    call(token,"restrictChatMember",{"chat_id":chat_id,"user_id":reply["from"]["id"],"permissions":{"can_send_messages":False}})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"🔇 كتم {reply['from'].get('first_name','')}"})
                if text in ["/unmute","فك الكتم"] and reply:
                    if not is_admin(token,chat_id,from_id):
                        continue
                    call(token,"restrictChatMember",{"chat_id":chat_id,"user_id":reply["from"]["id"],"permissions":{"can_send_messages":True,"can_send_media_messages":True,"can_send_other_messages":True,"can_add_web_page_previews":True}})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"🔊 فك كتم {reply['from'].get('first_name','')}"})
                if text in ["/pin","تثبيت"] and reply:
                    if not is_admin(token,chat_id,from_id):
                        continue
                    try:
                        call(token,"pinChatMessage",{"chat_id":chat_id,"message_id":reply["message_id"]})
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"📌 تم التثبيت"})
                    except:
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"❌ البوت ليس أدمن"})
                if text in ["/unpin","الغاء التثبيت"]:
                    if not is_admin(token,chat_id,from_id):
                        continue
                    try:
                        call(token,"unpinChatMessage",{"chat_id":chat_id})
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"📍 تم إلغاء التثبيت"})
                    except:
                        pass
                if text in ["/warn","تحذير"] and reply:
                    if not is_admin(token,chat_id,from_id):
                        continue
                    key=f"{chat_id}_{reply['from']['id']}"
                    warns[key]=warns.get(key,0)+1
                    c=warns[key]
                    if c>=3:
                        call(token,"banChatMember",{"chat_id":chat_id,"user_id":reply["from"]["id"]})
                        call(token,"sendMessage",{"chat_id":chat_id,"text":f"🔨 حظر {reply['from'].get('first_name','')} - 3 تحذيرات"})
                        warns[key]=0
                    else:
                        call(token,"sendMessage",{"chat_id":chat_id,"text":f"⚠️ تحذير {c}/3"})
                if raw.lower().startswith("/lock") or raw.startswith("قفل "):
                    if not is_admin(token,chat_id,from_id):
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"❌ أدمن فقط"})
                        continue
                    cfg=locks.get(str(chat_id),{})
                    what=raw.lower()
                    if "link" in what or "الروابط" in what:
                        cfg["links"]=True
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔒 قفل الروابط ✅"})
                    if "photo" in what or "الصور" in what:
                        cfg["photos"]=True
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔒 قفل الصور ✅"})
                    if "all" in what or "الكل" in what:
                        cfg={"links":True,"photos":True,"videos":True,"stickers":True}
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔒 قفل الكل ✅"})
                    locks[str(chat_id)]=cfg
                if raw.lower().startswith("/unlock") or raw.startswith("فتح "):
                    if not is_admin(token,chat_id,from_id):
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"❌ أدمن فقط"})
                        continue
                    cfg=locks.get(str(chat_id),{})
                    what=raw.lower()
                    if "link" in what or "الروابط" in what:
                        cfg["links"]=False
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔓 فتح الروابط ✅"})
                    if "all" in what or "الكل" in what:
                        cfg={}
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔓 فتح الكل ✅"})
                    locks[str(chat_id)]=cfg
        except Exception as e:
            print(f"Protection error {e}")
            time.sleep(2)

def run_downloader(token):
    me=call(token,"getMe")
    username=me.get("result",{}).get("username","") if me.get("ok") else ""
    setup_botfather_auto(token, "downloader", username)
    offset=0
    while True:
        try:
            res=call(token,"getUpdates",{"offset":offset,"timeout":25})
            for upd in res.get("result",[]):
                offset=upd["update_id"]+1
                msg=upd.get("message",{})
                chat_id=msg.get("chat",{}).get("id")
                raw=msg.get("text","") or ""
                if not chat_id:
                    continue
                text=clean_cmd(raw)
                if text=="/start":
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"✨ **بوت التحميل VIP**\n\n@{username}"})
                check=raw
                for p in ["/download ","/tiktok ","/youtube "]:
                    if check.startswith(p):
                        check=check.replace(p,"").strip()
                if "tiktok.com" in check:
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"⏳ جاري التحميل..."})
                    info=dl_tiktok(check)
                    if info["ok"]:
                        try:
                            call(token,"sendVideo",{"chat_id":chat_id,"video":info["url"]})
                        except:
                            call(token,"sendMessage",{"chat_id":chat_id,"text":info["url"]})
        except Exception as e:
            print(e)
            time.sleep(2)

RUNNERS={"protection":run_protection,"downloader":run_downloader}
pending={}
pending_type={}

def factory_loop():
    all_bots=load_bots()
    for username,info in all_bots.items():
        token=info.get("token")
        btype=info.get("type","protection")
        threading.Thread(target=RUNNERS.get(btype,run_protection),args=(token,),daemon=True).start()
    offset=0
    print("Factory VIP Ready")
    while True:
        try:
            res=call(FACTORY_TOKEN,"getUpdates",{"offset":offset,"timeout":25})
            for upd in res.get("result",[]):
                offset=upd["update_id"]+1
                if "callback_query" in upd:
                    cq=upd["callback_query"]
                    chat_id=cq["message"]["chat"]["id"]
                    user_id=cq["from"]["id"]
                    from_user=cq["from"]
                    data=cq["data"]
                    mid=cq["message"]["message_id"]
                    call(FACTORY_TOKEN,"answerCallbackQuery",{"callback_query_id":cq["id"]})
                    if data=="make_protection":
                        all_bots=load_bots()
                        is_prem, prem_info = is_premium_active(user_id)
                        max_allowed = prem_info.get("max_bots", 10) if is_prem else 1
                        if count_user_type(all_bots, user_id, "protection") >= max_allowed:
                            kb={"inline_keyboard":[[{"text":"💳 الاشتراكات - 3 باقات","callback_data":"subscriptions"}],[{"text":"📞 @mernaqueen","url":f"https://t.me/{DEV_USERNAME}"}]]}
                            call(FACTORY_TOKEN,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":"⚠️ وصلت للحد - اشترك","reply_markup":kb})
                            continue
                        pending_type[str(chat_id)]="protection"
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":"🔑 **صنع بوت حماية VIP**\n\n📍 @BotFather → /newbot\n📍 انسخ التوكن وارسله هنا فقط","parse_mode":"Markdown"})
                    elif data=="make_downloader":
                        pending_type[str(chat_id)]="downloader"
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":"🔑 **صنع بوت تحميل**\n\n📍 @BotFather → /newbot"})
                    elif data.startswith("type_"):
                        btype=data.replace("type_","")
                        key=str(chat_id)
                        if key not in pending:
                            continue
                        token=pending[key]
                        me=call(token,"getMe")
                        if not me.get("ok"):
                            call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":"❌ التوكن غلط"})
                            continue
                        bot_user=me["result"]["username"]
                        all_bots=load_bots()
                        is_prem, _ = is_premium_active(user_id)
                        all_bots[bot_user]={"token":token,"type":btype,"name":me["result"].get("first_name",""),"owner_id":user_id,"owner_username":from_user.get("username",""),"created_at":time.time(),"vip": is_prem}
                        save_bots(all_bots)
                        threading.Thread(target=RUNNERS.get(btype,run_protection),args=(token,),daemon=True).start()
                        del pending[key]
                        pending_type.pop(key,None)
                        kb={"inline_keyboard":[[{"text":f"🚀 @{bot_user}","url":f"https://t.me/{bot_user}"}],[{"text":"📊 بوتاتي","callback_data":"my_bots"}]]}
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":f"✅ تم صنع البوت @{bot_user}\n📦 {btype}\n🔗 ربط اوتوماتيك BotFather","reply_markup":kb})
                    elif data=="my_bots":
                        all_bots=load_bots()
                        user_bots=get_user_bots(all_bots, user_id)
                        if not user_bots:
                            kb={"inline_keyboard":[[{"text":"🛡️ صنع حماية","callback_data":"make_protection"}],[{"text":"📥 صنع تحميل","callback_data":"make_downloader"}]]}
                            call(FACTORY_TOKEN,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":"📭 لا يوجد بوتات","reply_markup":kb})
                        else:
                            txt="📊 **بوتاتك**\n\n"
                            btns=[]
                            for u,i in user_bots.items():
                                txt+=f"@{u} - {i.get('type')}\n"
                                btns.append([{"text":f"🗑️ حذف @{u}","callback_data":f"del_{u}"},{"text":f"🚀 فتح @{u}","url":f"https://t.me/{u}"}])
                            btns.append([{"text":"➕ إنشاء جديد","callback_data":"back_main"}])
                            btns.append([{"text":"💳 الاشتراكات","callback_data":"subscriptions"}])
                            call(FACTORY_TOKEN,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":{"inline_keyboard":btns}})
                    elif data.startswith("del_"):
                        bot_username=data.replace("del_","")
                        all_bots=load_bots()
                        if bot_username in all_bots and str(all_bots[bot_username].get("owner_id"))==str(user_id):
                            del all_bots[bot_username]
                            save_bots(all_bots)
                            call(FACTORY_TOKEN,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":f"🗑️ تم حذف @{bot_username}","reply_markup":{"inline_keyboard":[[{"text":"🔙 بوتاتي","callback_data":"my_bots"}]]}})
                    elif data=="subscriptions":
                        txt="💳 **الاشتراكات VIP**\n\n**الخانة 1: شهري**\n💰 99ج - خصم 33% - 3 بوتات\n\n**الخانة 2: 6 شهور ⭐️**\n💰 499ج - خصم 44% - 8 بوتات\n\n**الخانة 3: سنوي 👑**\n💰 799ج - خصم 55% - 15 بوت\n\n📞 @mernaqueen"
                        kb={"inline_keyboard":[[{"text":"📅 شهري - 99ج","callback_data":"sub_monthly"}],[{"text":"⭐️ 6 شهور - 499ج","callback_data":"sub_6months"}],[{"text":"👑 سنوي - 799ج","callback_data":"sub_yearly"}],[{"text":"📞 @mernaqueen","url":f"https://t.me/{DEV_USERNAME}"}],[{"text":"🔙 رجوع","callback_data":"back_main"}]]}
                        call(FACTORY_TOKEN,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb})
                    elif data=="back_main":
                        is_prem, _ = is_premium_active(user_id)
                        vip_badge = "💎 VIP" if is_prem else "🆓 مجاني"
                        kb={"inline_keyboard":[[{"text":"🛡️ صنع بوت حماية","callback_data":"make_protection"}],[{"text":"📥 صنع بوت تحميل","callback_data":"make_downloader"}],[{"text":f"📊 بوتاتي {vip_badge}","callback_data":"my_bots"},{"text":"💳 الاشتراكات","callback_data":"subscriptions"}],[{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]]}
                        call(FACTORY_TOKEN,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":f"⭐️ **مصنع ميمو VIP**\n\n{vip_badge}\n\n👇 اختر:","reply_markup":kb})
                    continue
                msg=upd.get("message",{})
                chat_id=msg.get("chat",{}).get("id")
                user_id=msg.get("from",{}).get("id")
                from_user=msg.get("from",{})
                text=msg.get("text","")
                if not chat_id:
                    continue
                if text.startswith("/addpremium"):
                    if not is_admin_user(from_user):
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":"❌ للأدمن فقط @mernaqueen"})
                        continue
                    try:
                        parts = text.split()
                        target = parts[1].replace("@","").strip()
                        tier = parts[2] if len(parts) > 2 else "monthly"
                        tier_map = {"monthly": {"days":30, "max_bots":3, "name":"شهري", "price":"99 جنيه"},"6months": {"days":180, "max_bots":8, "name":"6 شهور", "price":"499 جنيه"},"yearly": {"days":365, "max_bots":15, "name":"سنوي", "price":"799 جنيه"}}
                        tier_info = tier_map.get(tier.lower(), tier_map["monthly"])
                        target_id = target.lower() if not target.isdigit() else int(target)
                        premium = load_premium()
                        expire = time.time() + (tier_info["days"] * 24 * 3600)
                        premium[str(target_id)] = {"user_id": str(target_id),"username": target,"tier": tier_info["name"],"max_bots": tier_info["max_bots"],"expire": expire,"activated_by": from_user.get("username","admin")}
                        if not str(target_id).isdigit():
                            premium[target.lower()] = premium[str(target_id)]
                        save_premium(premium)
                        from datetime import datetime
                        expire_str = datetime.fromtimestamp(expire).strftime("%Y-%m-%d")
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":f"✅ تم التفعيل VIP\n\n@{target}\n💎 {tier_info['name']}\n📦 {tier_info['max_bots']} بوت\n📅 {expire_str}\n\n🔗 ربط اوتوماتيك"})
                    except Exception as e:
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":f"❌ خطأ: {e}"})
                if text=="/start":
                    is_prem, prem_info = is_premium_active(user_id)
                    vip_badge = f"💎 VIP {prem_info.get('tier','')}" if is_prem else "🆓 مجاني"
                    kb={"inline_keyboard":[[{"text":"🛡️ صنع بوت حماية","callback_data":"make_protection"}],[{"text":"📥 صنع بوت تحميل","callback_data":"make_downloader"}],[{"text":f"📊 بوتاتي {vip_badge}","callback_data":"my_bots"},{"text":"💳 الاشتراكات (3 باقات)","callback_data":"subscriptions"}],[{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]]}
                    call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":f"⭐️ **مصنع ميمو VIP**\n\n{vip_badge}\n\n👇 اختر:","reply_markup":kb})
                if text and len(text)>20 and ":" in text and " " not in text:
                    me=call(text,"getMe")
                    if me.get("ok"):
                        pending[str(chat_id)]=text
                        btype=pending_type.get(str(chat_id),"protection")
                        kb={"inline_keyboard":[[{"text":f"✅ تأكيد صنع {btype} VIP","callback_data":f"type_{btype}"}],[{"text":"❌ إلغاء","callback_data":"back_main"}]]}
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":f"✅ توكن @{me['result']['username']} صحيح\n🔗 ربط اوتوماتيك","reply_markup":kb})
                    else:
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":"❌ التوكن غلط"})
        except Exception as e:
            print(f"Factory error: {e}")
            time.sleep(2)

factory_loop()
