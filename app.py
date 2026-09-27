import json, os, threading, time, urllib.request, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

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

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        try:
            d = load_bots()
            msg = f"Factory Running Bots:{len(d)}"
            self.wfile.write(msg.encode())
        except:
            self.wfile.write(b"Factory Running")
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
        url = "https://api.telegram.org/bot" + token + "/" + method
        payload = None
        if data:
            payload = json.dumps(data).encode()
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

def is_admin(token, chat_id, user_id):
    r = call(token, "getChatMember", {"chat_id": chat_id, "user_id": user_id})
    s = r.get("result", {}).get("status", "")
    return s in ["administrator", "creator"]

def dl_tiktok(url):
    try:
        if REQ:
            r = requests.post("https://www.tikwm.com/api/", data={"url": url}, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
            j = r.json()
            if j.get("code") == 0:
                data = j.get("data", {})
                vurl = data.get("play") or data.get("hdplay")
                return {"ok": True, "url": vurl, "title": data.get("title","TikTok")}
    except Exception as e:
        print(e)
    return {"ok": False}

def dl_yt(url):
    try:
        if YTDLP:
            opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True, 'format': 'best'}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {"ok": True, "url": info.get("url"), "title": info.get("title","Video")}
    except Exception as e:
        print(e)
    return {"ok": False}

def run_protection(token):
    offset = 0
    locks = {}
    print("Protection started")
    while True:
        try:
            res = call(token, "getUpdates", {"offset": offset, "timeout": 25})
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat = msg.get("chat", {})
                chat_id = chat.get("id")
                chat_type = chat.get("type","")
                text = msg.get("text","") or msg.get("caption","")
                from_id = msg.get("from",{}).get("id")
                if not chat_id:
                    continue
                if chat_type!= "private" and text:
                    cfg = locks.get(str(chat_id), {})
                    if cfg.get("links"):
                        if "http" in text or "t.me" in text:
                            if not is_admin(token, chat_id, from_id):
                                call(token, "deleteMessage", {"chat_id": chat_id, "message_id": msg.get("message_id")})
                                continue
                if text == "/start" and chat_type == "private":
                    me = call(token, "getMe").get("result", {})
                    username = me.get("username","")
                    kb = {"inline_keyboard": [[{"text": "اضفني مجموعة", "url": "https://t.me/" + username + "?startgroup=new"}]]}
                    txt = "بوت حماية احترافي\n\nطرد / كتم / حظر بالرد\nقفل الروابط / فتح الروابط\nتثبيت\n\nضيفني مجموعة وارفعني ادمن واكتب تفعيل"
                    call(token, "sendMessage", {"chat_id": chat_id, "text": txt, "reply_markup": kb})
                if text in ["تفعيل", "تفعيل المجموعة"]:
                    txt = "تم تفعيل المجموعة\n\nالاوامر:\nطرد بالرد\nكتم بالرد\nتثبيت بالرد\nقفل الروابط\nفتح الروابط"
                    call(token, "sendMessage", {"chat_id": chat_id, "text": txt})
                if text in ["طرد", "كتم", "حظر"] and msg.get("reply_to_message"):
                    if not is_admin(token, chat_id, from_id):
                        continue
                    target = msg["reply_to_message"]["from"]["id"]
                    tname = msg["reply_to_message"]["from"]["first_name"]
                    if text == "طرد":
                        call(token, "banChatMember", {"chat_id": chat_id, "user_id": target})
                        call(token, "unbanChatMember", {"chat_id": chat_id, "user_id": target})
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم طرد " + tname})
                    if text == "كتم":
                        perms = {"can_send_messages": False}
                        call(token, "restrictChatMember", {"chat_id": chat_id, "user_id": target, "permissions": perms})
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم كتم " + tname})
                    if text == "حظر":
                        call(token, "banChatMember", {"chat_id": chat_id, "user_id": target})
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم حظر " + tname})
                if text.startswith("قفل "):
                    cfg = locks.get(str(chat_id), {})
                    if "الرابط" in text:
                        cfg["links"] = True
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم قفل الروابط"})
                    locks[str(chat_id)] = cfg
                if text.startswith("فتح "):
                    cfg = locks.get(str(chat_id), {})
                    if "الرابط" in text:
                        cfg["links"] = False
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم فتح الروابط"})
                    locks[str(chat_id)] = cfg
        except Exception as e:
            print(e)
            time.sleep(2)

def run_downloader(token):
    offset = 0
    print("Downloader started")
    while True:
        try:
            res = call(token, "getUpdates", {"offset": offset, "timeout": 25})
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                if not chat_id:
                    continue
                if text == "/start":
                    txt = "بوت التحميل الحقيقي\n\nيدعم:\nتيك توك بدون علامة\nيوتيوب\nانستجرام\nتويتر\nفيسبوك\n\nابعت الرابط الآن"
                    call(token, "sendMessage", {"chat_id": chat_id, "text": txt})
                if "tiktok.com" in text:
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "جاري تحميل تيك توك حقيقي..."})
                    info = dl_tiktok(text)
                    if info["ok"] and info.get("url"):
                        try:
                            call(token, "sendVideo", {"chat_id": chat_id, "video": info["url"], "caption": info.get("title","")})
                        except:
                            call(token, "sendMessage", {"chat_id": chat_id, "text": info["url"]})
                    else:
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "فشل - جرب رابط تاني"})
                if "youtube.com" in text or "youtu.be" in text or "instagram.com" in text or "twitter.com" in text or "x.com" in text or "facebook.com" in text:
                    if "tiktok.com" in text:
                        continue
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "جاري التحميل الحقيقي..."})
                    info = dl_yt(text)
                    if info["ok"] and info.get("url"):
                        try:
                            call(token, "sendVideo", {"chat_id": chat_id, "video": info["url"], "caption": info.get("title","")})
                        except:
                            call(token, "sendMessage", {"chat_id": chat_id, "text": info["url"]})
                    else:
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "لازم تثبت yt-dlp في requirements.txt"})
        except Exception as e:
            print(e)
            time.sleep(2)

def run_allinone(token):
    offset = 0
    print("AllInOne started")
    while True:
        try:
            res = call(token, "getUpdates", {"offset": offset, "timeout": 25})
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "") or ""
                if not chat_id:
                    continue
                if text == "/start":
                    txt = "البوت الشامل المحترم\n\nحماية + تحميل حقيقي\n\nابعت رابط تيك توك / يوتيوب / انستا\nاو اكتب تفعيل لو في مجموعة"
                    call(token, "sendMessage", {"chat_id": chat_id, "text": txt})
                if "tiktok.com" in text:
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "بحمل تيك توك حقيقي..."})
                    info = dl_tiktok(text)
                    if info["ok"] and info.get("url"):
                        try:
                            call(token, "sendVideo", {"chat_id": chat_id, "video": info["url"], "caption": info.get("title","")})
                        except:
                            call(token, "sendMessage", {"chat_id": chat_id, "text": info["url"]})
                if "youtube.com" in text or "youtu.be" in text or "instagram.com" in text:
                    if "tiktok.com" in text:
                        continue
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "بحمل حقيقي..."})
                    info = dl_yt(text)
                    if info["ok"] and info.get("url"):
                        try:
                            call(token, "sendVideo", {"chat_id": chat_id, "video": info["url"], "caption": info.get("title","")})
                        except:
                            call(token, "sendMessage", {"chat_id": chat_id, "text": info["url"]})
                if text in ["تفعيل", "تفعيل المجموعة"]:
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "تم التفعيل\nطرد / كتم / حظر بالرد"})
                if text in ["طرد", "كتم", "حظر"] and msg.get("reply_to_message"):
                    target = msg["reply_to_message"]["from"]["id"]
                    tname = msg["reply_to_message"]["from"]["first_name"]
                    if text == "طرد":
                        call(token, "banChatMember", {"chat_id": chat_id, "user_id": target})
                        call(token, "unbanChatMember", {"chat_id": chat_id, "user_id": target})
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم طرد " + tname})
        except Exception as e:
            print(e)
            time.sleep(2)

RUNNERS = {
    "protection": run_protection,
    "downloader": run_downloader,
    "allinone": run_allinone,
    "music": run_downloader,
    "movies": run_downloader
}

pending = {}

def factory_loop():
    bots = load_bots()
    for username, info in bots.items():
        token = info.get("token")
        btype = info.get("type", "allinone")
        runner = RUNNERS.get(btype, run_allinone)
        threading.Thread(target=runner, args=(token,), daemon=True).start()

    offset = 0
    print("Factory FIXED Ready")
    while True:
        try:
            res = call(FACTORY_TOKEN, "getUpdates", {"offset": offset, "timeout": 25})
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                if "callback_query" in upd:
                    cq = upd["callback_query"]
                    chat_id = cq.get("message", {}).get("chat", {}).get("id")
                    data = cq.get("data", "")
                    call(FACTORY_TOKEN, "answerCallbackQuery", {"callback_query_id": cq["id"]})
                    if data == "factory_begin":
                        call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": "ارسل توكن البوت من BotFather"})
                    if data.startswith("type_"):
                        btype = data.replace("type_", "")
                        key = str(chat_id)
                        if key not in pending:
                            continue
                        token = pending[key]
                        me = call(token, "getMe")
                        if not me.get("ok"):
                            continue
                        bot_user = me["result"]["username"]
                        bots = load_bots()
                        bots[bot_user] = {"token": token, "type": btype}
                        save_bots(bots)
                        runner = RUNNERS.get(btype, run_allinone)
                        threading.Thread(target=runner, args=(token,), daemon=True).start()
                        del pending[key]
                        kb = {"inline_keyboard": [[{"text": "روح للبوت @" + bot_user, "url": "https://t.me/" + bot_user}]]}
                        txt = "تم صنع @" + bot_user + " نوع " + btype + " بنجاح\nجرب ابعت رابط تيك توك"
                        call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": txt, "reply_markup": kb})
                    continue
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                if not chat_id:
                    continue
                if text == "/start":
                    kb = {"inline_keyboard": [[{"text": "صنع بوت محترم", "callback_data": "factory_begin"}]]}
                    txt = "مصنع Memoo PRO MAX FIXED\n\nحماية + تحميل حقيقي\nتيك توك بدون علامة\nيوتيوب / انستا / تويتر\n\nدوس صنع بوت"
                    call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": txt, "reply_markup": kb})
                if text and len(text) > 20 and ":" in text and " " not in text:
                    me = call(text, "getMe")
                    if me.get("ok"):
                        pending[str(chat_id)] = text
                        kb = {"inline_keyboard": [
                            [{"text": "حماية", "callback_data": "type_protection"}],
                            [{"text": "تحميل حقيقي", "callback_data": "type_downloader"}],
                            [{"text": "شامل محترم", "callback_data": "type_allinone"}]
                        ]}
                        uname = me["result"]["username"]
                        txt = "توكن @" + uname + " صح\nاختر النوع"
                        call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": txt, "reply_markup": kb})
                    else:
                        call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": "التوكن غلط"})
        except Exception as e:
            print(e)
            time.sleep(2)

factory_loop()
