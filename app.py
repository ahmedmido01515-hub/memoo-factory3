import json, os, threading, time, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

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
        self.wfile.write(b"Memo Factory VIP - Auto BotFather")
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
    except:
        return {"ok": False}

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
    if info.get("expire", 0) > time.time():
        return True, info
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
            long_desc = f"✨ بوت الحماية المميز - سورس ميمو\n\n🤖 @{username}\n🛡️ حماية احترافية + VIP\n📢 @{CHANNEL}\n👨‍💻 @{DEV_USERNAME}\n\n⭐️ خليك مميز ونصب بوت حماية باسمك"
            call(token, "setMyShortDescription", {"short_description": short})
            call(token, "setMyDescription", {"description": long_desc})
            cmds=[
                {"command":"start","description":"✨ بداية البوت VIP"},
                {"command":"help","description":"📚 الأقسام المقسمة"},
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
            long_desc = f"✨ بوت التحميل المميز\n\n🤖 @{username}\n📥 تيك توك/يوتيوب/انستا"
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
                    kb={"inline_keyboard":[[{"text":"➕ أضفني لمجموعتك","url":f"https://t.me/{username}?startgroup=new"}],[{"text":"📚 الأقسام","callback_data":"help_main"}],[{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]]}
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
                    warns[key]=warns.get(key,
