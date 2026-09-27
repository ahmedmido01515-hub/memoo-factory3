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
            self.wfile.write(f"Factory FINAL PRO - Bots:{len(d)} - YTDLP:{YTDLP} - Commands:ON".encode())
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
                return {"ok": True, "url": vurl, "title": data.get("title","TikTok"), "author": data.get("author",{}).get("nickname","")}
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

def set_commands(token, btype):
    try:
        if btype == "protection":
            cmds = [
                {"command": "start", "description": "بداية البوت - ترحيب"},
                {"command": "help", "description": "عرض كل الاوامر"},
                {"command": "ping", "description": "فحص حالة البوت"},
                {"command": "id", "description": "معرفة ايديك وايدي الشات"},
                {"command": "info", "description": "معلومات المستخدم بالرد"},
                {"command": "whoami", "description": "معلوماتك انت"},
                {"command": "group", "description": "معلومات المجموعة"},
                {"command": "locks", "description": "عرض الاقفال النشطة"},
                {"command": "rules", "description": "عرض القوانين"},
                {"command": "settings", "description": "اعدادات المجموعة"},
                {"command": "ban", "description": "حظر مستخدم بالرد"},
                {"command": "unban", "description": "فك الحظر"},
                {"command": "kick", "description": "طرد مستخدم بالرد"},
                {"command": "mute", "description": "كتم مستخدم بالرد"},
                {"command": "unmute", "description": "فك الكتم"},
                {"command": "warn", "description": "تحذير مستخدم"},
                {"command": "unwarn", "description": "ازالة تحذير"},
                {"command": "warns", "description": "عرض تحذيرات المستخدم"},
                {"command": "pin", "description": "تثبيت رسالة بالرد"},
                {"command": "unpin", "description": "الغاء التثبيت"},
                {"command": "clear", "description": "مسح رسائل (عدد)"},
                {"command": "purge", "description": "حذف رسائل بالرد"},
                {"command": "lock", "description": "قفل نوع (رابط/صورة..)"},
                {"command": "unlock", "description": "فتح نوع"},
                {"command": "lockall", "description": "قفل كل الانواع"},
                {"command": "unlockall", "description": "فتح كل الانواع"},
                {"command": "promote", "description": "رفع ادمن بالرد"},
                {"command": "demote", "description": "تنزيل ادمن"},
                {"command": "setwelcome", "description": "تعيين رسالة ترحيب"},
                {"command": "setrules", "description": "تعيين القوانين"}
            ]
        elif btype == "downloader":
            cmds = [
                {"command": "start", "description": "بداية بوت التحميل"},
                {"command": "help", "description": "شرح الاستخدام"},
                {"command": "download", "description": "تحميل رابط - /download رابط"},
                {"command": "tiktok", "description": "تحميل تيك توك بدون علامة"},
                {"command": "youtube", "description": "تحميل يوتيوب MP4/MP3"},
                {"command": "instagram", "description": "تحميل انستجرام ريلز"},
                {"command": "twitter", "description": "تحميل تويتر X"},
                {"command": "facebook", "description": "تحميل فيسبوك"},
                {"command": "info", "description": "معلوماتك واحصائياتك"},
                {"command": "autodl", "description": "تفعيل التحميل التلقائي"}
            ]
        else:
            cmds = [
                {"command": "start", "description": "القائمة الرئيسية"},
                {"command": "help", "description": "كل الاوامر"},
                {"command": "ping", "description": "حالة البوت"},
                {"command": "id", "description": "ايديك"},
                {"command": "info", "description": "معلومات المستخدم"},
                {"command": "download", "description": "تحميل اي رابط"},
                {"command": "tiktok", "description": "تحميل تيك توك بدون علامة"},
                {"command": "youtube", "description": "تحميل يوتيوب"},
                {"command": "instagram", "description": "تحميل انستا"},
                {"command": "facebook", "description": "تحميل فيسبوك"},
                {"command": "twitter", "description": "تحميل تويتر"},
                {"command": "ban", "description": "حظر بالرد - جروبات"},
                {"command": "unban", "description": "فك الحظر"},
                {"command": "kick", "description": "طرد بالرد"},
                {"command": "mute", "description": "كتم بالرد"},
                {"command": "unmute", "description": "فك الكتم"},
                {"command": "warn", "description": "تحذير"},
                {"command": "pin", "description": "تثبيت رسالة"},
                {"command": "unpin", "description": "الغاء التثبيت"},
                {"command": "lock", "description": "قفل (رابط/صورة/فيديو)"},
                {"command": "unlock", "description": "فتح"},
                {"command": "lockall", "description": "قفل الكل"},
                {"command": "unlockall", "description": "فتح الكل"},
                {"command": "locks", "description": "عرض الاقفال"},
                {"command": "rules", "description": "القوانين"},
                {"command": "settings", "description": "الاعدادات"},
                {"command": "setrules", "description": "وضع قوانين"},
                {"command": "setwelcome", "description": "وضع ترحيب"},
                {"command": "promote", "description": "رفع ادمن"},
                {"command": "demote", "description": "تنزيل ادمن"},
                {"command": "clear", "description": "مسح رسائل"}
            ]
        call(token, "setMyCommands", {"commands": cmds})
        print(f"Commands set for {btype}: {len(cmds)}")
    except Exception as e:
        print(f"set commands error: {e}")

def run_protection(token):
    set_commands(token, "protection")
    offset = 0
    locks = {}
    warns = {}
    print("Protection FINAL started")
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
                reply = msg.get("reply_to_message")
                if not chat_id:
                    continue
                if chat_type!= "private":
                    cfg = locks.get(str(chat_id), {})
                    if from_id and not is_admin(token, chat_id, from_id):
                        if cfg.get("links") and ("http" in text or "t.me/" in text or "@" in text):
                            call(token, "deleteMessage", {"chat_id": chat_id, "message_id": msg.get("message_id")})
                            continue
                        if cfg.get("photos") and msg.get("photo"):
                            call(token, "deleteMessage", {"chat_id": chat_id, "message_id": msg.get("message_id")})
                            continue
                        if cfg.get("videos") and msg.get("video"):
                            call(token, "deleteMessage", {"chat_id": chat_id, "message_id": msg.get("message_id")})
                            continue
                        if cfg.get("stickers") and msg.get("sticker"):
                            call(token, "deleteMessage", {"chat_id": chat_id, "message_id": msg.get("message_id")})
                            continue
                if text in ["/start", "start"]:
                    me = call(token, "getMe").get("result", {})
                    username = me.get("username","")
                    kb = {"inline_keyboard": [[{"text": "اضفني مجموعة + رفع ادمن", "url": "https://t.me/" + username + "?startgroup=new"}], [{"text": "اوامر الحماية", "callback_data": "help_pro"}]]}
                    txt = "بوت الحماية الاحترافي\n\nقايمة الاوامر (اكتب / ): \n/start - البداية\n/help - كل الاوامر\n/ban - حظر بالرد\n/kick - طرد بالرد\n/mute - كتم بالرد\n/unmute - فك الكتم\n/warn - تحذير\n/pin - تثبيت\n/lock - قفل\n/unlock - فتح\n/rules - القوانين\n\nبالعربي:\nتفعيل - تعطيل - طرد - كتم - حظر - تثبيت - قفل الروابط"
                    call(token, "sendMessage", {"chat_id": chat_id, "text": txt, "reply_markup": kb})
                if text in ["/help", "help", "/اوامر"]:
                    txt = "اوامر الحماية الكاملة:\n\n/start - البداية\n/ping - حالة البوت\n/id - ايديك\n/info - معلومات بالرد\n/whoami - معلوماتك\n/group - معلومات المجموعة\n/locks - الاقفال النشطة\n/rules - القوانين\n/settings - الاعدادات\n\n/ban - حظر بالرد\n/unban - فك الحظر\n/kick - طرد\n/mute - كتم\n/unmute - فك الكتم\n/warn - تحذير\n/unwarn - ازالة تحذير\n/warns - عرض التحذيرات\n/pin - تثبيت\n/unpin - الغاء التثبيت\n/clear - مسح رسائل\n/purge - حذف بالرد\n/lock links - قفل الروابط\n/unlock links - فتح الروابط\n/lock photos - قفل الصور\n/lock videos - قفل الفيديو\n/lock stickers - قفل الملصقات\n/lockall - قفل الكل\n/unlockall - فتح الكل\n/promote - رفع ادمن\n/demote - تنزيل ادمن\n/setwelcome - وضع ترحيب\n/setrules - وضع قوانين\n\nتفعيل - لتفعيل المجموعة"
                    call(token, "sendMessage", {"chat_id": chat_id, "text": txt})
                if text == "/ping":
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "البوت شغال - Pong!"})
                if text in ["/id", "ايدي"]:
                    txt = f"ايديك: {from_id}\nايدي الشات: {chat_id}"
                    if reply:
                        txt += f"\nايدي المردود عليه: {reply['from']['id']}"
                    call(token, "sendMessage", {"chat_id": chat_id, "text": txt})
                if text in ["تفعيل", "تفعيل المجموعة", "/activate", "/تفعيل"]:
                    if chat_type == "private":
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "ضيفني مجموعة وارفعني ادمن واكتب تفعيل"})
                    else:
                        if not is_admin(token, chat_id, from_id):
                            call(token, "sendMessage", {"chat_id": chat_id, "text": "لازم تكون ادمن"})
                        else:
                            call(token, "sendMessage", {"chat_id": chat_id, "text": f"تم تفعيل المجموعة {chat.get('title')}\n\n/ban - حظر\n/kick - طرد\n/mute - كتم\n/pin - تثبيت\n/lock - قفل"})
                if text in ["طرد", "/kick", "/طرد"] and reply:
                    if not is_admin(token, chat_id, from_id):
                        continue
                    target = reply["from"]["id"]
                    tname = reply["from"]["first_name"]
                    call(token, "banChatMember", {"chat_id": chat_id, "user_id": target})
                    call(token, "unbanChatMember", {"chat_id": chat_id, "user_id": target})
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "تم طرد " + tname})
                if text in ["كتم", "/mute", "/كتم"] and reply:
                    if not is_admin(token, chat_id, from_id):
                        continue
                    target = reply["from"]["id"]
                    tname = reply["from"]["first_name"]
                    perms = {"can_send_messages": False}
                    call(token, "restrictChatMember", {"chat_id": chat_id, "user_id": target, "permissions": perms})
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "تم كتم " + tname})
                if text in ["حظر", "/ban", "/حظر"] and reply:
                    if not is_admin(token, chat_id, from_id):
                        continue
                    target = reply["from"]["id"]
                    tname = reply["from"]["first_name"]
                    call(token, "banChatMember", {"chat_id": chat_id, "user_id": target})
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "تم حظر " + tname})
                if text in ["/unban", "فك الحظر"] and reply:
                    if not is_admin(token, chat_id, from_id):
                        continue
                    target = reply["from"]["id"]
                    call(token, "unbanChatMember", {"chat_id": chat_id, "user_id": target})
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "تم فك الحظر"})
                if text in ["/unmute", "فك الكتم"] and reply:
                    if not is_admin(token, chat_id, from_id):
                        continue
                    target = reply["from"]["id"]
                    perms = {"can_send_messages": True, "can_send_media_messages": True, "can_send_other_messages": True, "can_add_web_page_previews": True}
                    call(token, "restrictChatMember", {"chat_id": chat_id, "user_id": target, "permissions": perms})
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "تم فك الكتم"})
                if text in ["تثبيت", "/pin", "/تثبيت"] and reply:
                    if not is_admin(token, chat_id, from_id):
                        continue
                    try:
                        call(token, "pinChatMessage", {"chat_id": chat_id, "message_id": reply["message_id"]})
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم التثبيت"})
                    except:
                        pass
                if text in ["/unpin", "الغاء التثبيت"]:
                    if not is_admin(token, chat_id, from_id):
                        continue
                    try:
                        call(token, "unpinChatMessage", {"chat_id": chat_id})
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم الغاء التثبيت"})
                    except:
                        pass
                if text.startswith("/warn") or text == "تحذير":
                    if not is_admin(token, chat_id, from_id):
                        continue
                    if reply:
                        target = reply["from"]["id"]
                        key = f"{chat_id}_{target}"
                        warns[key] = warns.get(key, 0) + 1
                        count = warns[key]
                        if count >= 3:
                            call(token, "banChatMember", {"chat_id": chat_id, "user_id": target})
                            call(token, "sendMessage", {"chat_id": chat_id, "text": f"تم حظر {reply['from']['first_name']} - 3 تحذيرات"})
                            warns[key] = 0
                        else:
                            call(token, "sendMessage", {"chat_id": chat_id, "text": f"تحذير {count}/3 لـ {reply['from']['first_name']}"})
                if text.startswith("/lock") or text.startswith("قفل "):
                    if not is_admin(token, chat_id, from_id):
                        continue
                    cfg = locks.get(str(chat_id), {})
                    what = text.lower()
                    if "link" in what or "الرابط" in what:
                        cfg["links"] = True
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم قفل الروابط"})
                    if "photo" in what or "الصور" in what:
                        cfg["photos"] = True
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم قفل الصور"})
                    if "video" in what or "الفيديو" in what:
                        cfg["videos"] = True
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم قفل الفيديو"})
                    if "sticker" in what or "الملصق" in what:
                        cfg["stickers"] = True
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم قفل الملصقات"})
                    if "all" in what or "الكل" in what:
                        cfg = {"links": True, "photos": True, "videos": True, "stickers": True}
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم قفل الكل"})
                    locks[str(chat_id)] = cfg
                if text.startswith("/unlock") or text.startswith("فتح "):
                    if not is_admin(token, chat_id, from_id):
                        continue
                    cfg = locks.get(str(chat_id), {})
                    what = text.lower()
                    if "link" in what or "الرابط" in what:
                        cfg["links"] = False
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم فتح الروابط"})
                    if "photo" in what or "الصور" in what:
                        cfg["photos"] = False
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم فتح الصور"})
                    if "all" in what or "الكل" in what:
                        cfg = {}
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "تم فتح الكل"})
                    locks[str(chat_id)] = cfg
                if text in ["/locks", "الاقفال"]:
                    cfg = locks.get(str(chat_id), {})
                    txt = "الاقفال:\n"
                    txt += f"الروابط: {'مقفول' if cfg.get('links') else 'مفتوح'}\n"
                    txt += f"الصور: {'مقفول' if cfg.get('photos') else 'مفتوح'}\n"
                    txt += f"الفيديو: {'مقفول' if cfg.get('videos') else 'مفتوح'}\n"
                    txt += f"الملصقات: {'مقفول' if cfg.get('stickers') else 'مفتوح'}"
                    call(token, "sendMessage", {"chat_id": chat_id, "text": txt})
        except Exception as e:
            print(e)
            time.sleep(2)

def run_downloader(token):
    set_commands(token, "downloader")
    offset = 0
    print("Downloader FINAL started")
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
                    txt = "بوت التحميل الخارق الحقيقي\n\nقايمة الاوامر /:\n/start - البداية\n/help - المساعدة\n/download رابط - تحميل\n/tiktok - تحميل تيك توك بدون علامة\n/youtube - تحميل يوتيوب\n/instagram - تحميل انستا\n/twitter - تحميل تويتر\n/facebook - تحميل فيسبوك\n/info - احصائياتك\n\nابعت رابط الآن وهحمله حقيقي"
                    call(token, "sendMessage", {"chat_id": chat_id, "text": txt})
                if text == "/help":
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "ابعت رابط من:\nتيك توك - يوتيوب - انستا - تويتر - فيسبوك\n\nمثال:\nhttps://www.tiktok.com/@user/video/123\nhttps://youtu.be/xyz\n\nوهحمله بدون علامة"})
                if text.startswith("/download "):
                    url = text.replace("/download ", "").strip()
                    text = url
                if "tiktok.com" in text:
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "جاري تحميل تيك توك حقيقي بدون علامة..."})
                    info = dl_tiktok(text)
                    if info["ok"] and info.get("url"):
                        try:
                            call(token, "sendVideo", {"chat_id": chat_id, "video": info["url"], "caption": f"{info.get('title','')} - {info.get('author','')}"})
                        except:
                            call(token, "sendMessage", {"chat_id": chat_id, "text": info["url"]})
                    else:
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "فشل - جرب رابط تاني"})
                if "youtube.com" in text or "youtu.be" in text or "instagram.com" in text or "twitter.com" in text or "x.com" in text or "facebook.com" in text or "fb.watch" in text:
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
                        call(token, "sendMessage", {"chat_id": chat_id, "text": "لازم تثبت yt-dlp في requirements.txt\nحط: yt-dlp\nrequests"})
        except Exception as e:
            print(e)
            time.sleep(2)

def run_allinone(token):
    set_commands(token, "allinone")
    offset = 0
    locks = {}
    print("AllInOne FINAL started")
    while True:
        try:
            res = call(token, "getUpdates", {"offset": offset, "timeout": 25})
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "") or ""
                reply = msg.get("reply_to_message")
                from_id = msg.get("from",{}).get("id")
                if not chat_id:
                    continue
                if text == "/start":
                    txt = "البوت الشامل المحترم FINAL\n\nقايمة الاوامر /:\n/download - تحميل اي رابط\n/tiktok - تيك توك بدون علامة\n/youtube - يوتيوب\n/instagram - انستا\n/ban - حظر بالرد\n/kick - طرد بالرد\n/mute - كتم\n/pin - تثبيت\n/lock - قفل\n/unlock - فتح\n/rules - القوانين\n/settings - الاعدادات\n\nابعت رابط او ضيفني مجموعة واكتب تفعيل"
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
                if text in ["تفعيل", "/activate"]:
                    call(token, "sendMessage", {"chat_id": chat_id, "text": "تم التفعيل\n/ban /kick /mute بالرد\n/lock /unlock"})
                if text in ["طرد", "/kick"] and reply:
                    target = reply["from"]["id"]
                    tname = reply["from"]["first_name"]
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
    print("Factory FINAL with Commands Ready")
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
                        call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": "ارسل توكن البوت من @BotFather\nمثال: 123456:ABC..."})
                    if data.startswith("type_"):
                        btype = data.replace("type_", "")
                        key = str(chat_id)
                        if key not in pending:
                            continue
                        token = pending[key]
                        me = call(token, "getMe")
                        if not me.get("ok"):
                            call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": "التوكن غلط"})
                            continue
                        bot_user = me["result"]["username"]
                        bots = load_bots()
                        bots[bot_user] = {"token": token, "type": btype, "name": me["result"].get("first_name","")}
                        save_bots(bots)
                        runner = RUNNERS.get(btype, run_allinone)
                        threading.Thread(target=runner, args=(token,), daemon=True).start()
                        del pending[key]
                        kb = {"inline_keyboard": [[{"text": "روح للبوت @" + bot_user, "url": "https://t.me/" + bot_user}]]}
                        txt = f"تم صنع @{bot_user} نوع {btype} بنجاح\n\nالآن فيه قايمة اوامر / حقيقية\n{30 if btype=='protection' else 10} امر\n\nجرب /start هناك وهتلاقي القايمة ظهرت زي بوتات تليجرام المحترفة"
                        call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": txt, "reply_markup": kb})
                    continue
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                if not chat_id:
                    continue
                if text == "/start":
                    kb = {"inline_keyboard": [[{"text": "صنع بوت محترم بقايمة اوامر حقيقية", "callback_data": "factory_begin"}], [{"text": "الاوامر", "callback_data": "cmds_info"}]]}
                    txt = "مصنع Memoo FINAL PRO MAX - مع قايمة اوامر حقيقية\n\nفحص شامل لكل بوتات تليجرام:\n\nحماية (30 امر):\n/ban /kick /mute /warn /pin /lock /unlockall /promote /setrules...\n\nتحميل (10 اوامر):\n/download /tiktok /youtube /instagram /twitter /facebook...\n\nشامل (31 امر):\nكل اللي فوق مع بعض\n\nكل بوت مصنوع فيه setMyCommands حقيقي ويظهر لما تدوس /\n\nدوس صنع بوت"
                    call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": txt, "reply_markup": kb})
                if text and len(text) > 20 and ":" in text and " " not in text:
                    me = call(text, "getMe")
                    if me.get("ok"):
                        pending[str(chat_id)] = text
                        kb = {"inline_keyboard": [[{"text": "حماية 30 امر", "callback_data": "type_protection"}], [{"text": "تحميل 10 اوامر حقيقي", "callback_data": "type_downloader"}], [{"text": "شامل 31 امر حقيقي", "callback_data": "type_allinone"}]]}
                        uname = me["result"]["username"]
                        txt = f"توكن @{uname} صح\nاختر النوع - كلهم بقايمة اوامر / حقيقية"
                        call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": txt, "reply_markup": kb})
                    else:
                        call(FACTORY_TOKEN, "sendMessage", {"chat_id": chat_id, "text": "التوكن غلط - تأكد من @BotFather"})
        except Exception as e:
            print(e)
            time.sleep(2)

factory_loop()
