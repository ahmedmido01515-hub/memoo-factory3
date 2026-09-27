import json, os, threading, time, urllib.request, urllib.parse, re
from http.server import HTTPServer, BaseHTTPRequestHandler

# حاول استيراد yt-dlp لو موجود (هيشتغل على Railway لو ضفته في requirements.txt)
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except:
    YTDLP_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except:
    REQUESTS_AVAILABLE = False

FACTORY_TOKEN = os.getenv("TOKEN") or os.getenv("FACTORY_TOKEN") or "8835297704:AAHwG3vBZEMly31PH-WqBFLUXhebU_LMUEA"
DATA_FILE = "bots_pro.json"

# ===== سيرفر وهمي =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        try:
            data = load_bots()
            self.wfile.write(f"🏭 Memo PRO MAX REAL API - Bots: {len(data)} - Ready".encode())
        except:
            self.wfile.write(b"Factory Running")
    def log_message(self,*a): pass

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
        req_data = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=req_data, headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def load_bots():
    if os.path.exists(DATA_FILE):
        try: return json.load(open(DATA_FILE,"r",encoding="utf-8"))
        except: return {}
    return {}

def save_bots(d):
    json.dump(d, open(DATA_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

def is_admin(token, chat_id, user_id):
    res = call(token, "getChatMember", {"chat_id": chat_id, "user_id": user_id})
    return res.get("result",{}).get("status","") in ["administrator","creator"]

# ===================== دوال التحميل الحقيقية بـ API =====================

def download_tiktok_real(url):
    """تحميل تيك توك حقيقي بدون علامة مائية عبر TikWM API المجاني"""
    try:
        if REQUESTS_AVAILABLE:
            r = requests.post("https://www.tikwm.com/api/", data={"url": url}, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
            j = r.json()
            if j.get("code") == 0:
                data = j.get("data",{})
                return {
                    "ok": True,
                    "video_url": data.get("play") or data.get("hdplay"),
                    "music_url": data.get("music"),
                    "cover": data.get("cover"),
                    "title": data.get("title","TikTok Video"),
                    "author": data.get("author",{}).get("nickname","")
                }
        data = urllib.parse.urlencode({"url": url}).encode()
        req = urllib.request.Request("https://www.tikwm.com/api/", data=data, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            j = json.loads(resp.read().decode())
            if j.get("code") == 0:
                d = j.get("data",{})
                return {"ok": True, "video_url": d.get("play"), "title": d.get("title","TikTok")}
    except Exception as e:
        print(f"tiktok api error: {e}")
    return {"ok": False}

def download_youtube_real(url, audio_only=False):
    try:
        if YTDLP_AVAILABLE:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best' if audio_only else 'best[ext=mp4]/best',
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "ok": True,
                    "video_url": info.get("url"),
                    "title": info.get("title"),
                    "thumbnail": info.get("thumbnail"),
                    "duration": info.get("duration"),
                }
        if REQUESTS_AVAILABLE:
            payload = {"url": url, "vQuality": "720", "aFormat": "mp3" if audio_only else "mp4", "isAudioOnly": audio_only}
            r = requests.post("https://api.cobalt.tools/api/json", json=payload, headers={"Accept":"application/json","Content-Type":"application/json"}, timeout=20)
            j = r.json()
            if j.get("status") == "redirect" or "url" in j:
                return {"ok": True, "video_url": j.get("url"), "title": "YouTube Video"}
    except Exception as e:
        print(f"youtube error: {e}")
    return {"ok": False}

def download_instagram_real(url):
    try:
        if YTDLP_AVAILABLE:
            ydl_opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if "entries" in info:
                    info = info["entries"][0]
                return {"ok": True, "video_url": info.get("url"), "title": info.get("title") or "Instagram"}
    except Exception as e:
        print(f"insta error: {e}")
    return {"ok": False}

def download_generic_real(url):
    try:
        if YTDLP_AVAILABLE:
            ydl_opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True, 'format': 'best'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {"ok": True, "video_url": info.get("url"), "title": info.get("title","Video")}
    except Exception as e:
        print(f"generic error: {e}")
    return {"ok": False}

# ===================== بوتات محترمة =====================

def run_protection_bot(token):
    offset=0
    locks={}
    while True:
        try:
            res = call(token,"getUpdates",{"offset":offset,"timeout":25})
            for upd in res.get("result",[]):
                offset = upd["update_id"]+1
                msg = upd.get("message",{})
                chat_id = msg.get("chat",{}).get("id")
                chat_type = msg.get("chat",{}).get("type","")
                text = msg.get("text","") or msg.get("caption","")
                from_id = msg.get("from",{}).get("id")
                if not chat_id: continue
                if text=="/start" and chat_type=="private":
                    me = call(token,"getMe").get("result",{})
                    kb = {"inline_keyboard":[[{"text":"🛡️ اضفني مجموعة","url":f"https://t.me/{me.get('username')}?startgroup=new"}]]}
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"🛡️ بوت حماية احترافي\n✅ طرد/كتم/حظر بالرد\n✅ قفل روابط/صور\n✅ تثبيت\n\nضيفني مجموعة وارفعني ادمن واكتب تفعيل\n@{me.get('username')}","reply_markup":kb})
                elif text in ["تفعيل","تفعيل المجموعة"]:
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"✅ تم تفعيل المجموعة\n\n• طرد بالرد\n• كتم بالرد\n• تثبيت\n• قفل الروابط / فتح الروابط"})
                elif text in ["طرد","كتم","حظر"] and msg.get("reply_to_message"):
                    target = msg["reply_to_message"]["from"]["id"]
                    name = msg["reply_to_message"]["from"]["first_name"]
                    if text=="طرد":
                        call(token,"banChatMember",{"chat_id":chat_id,"user_id":target})
                        call(token,"unbanChatMember",{"chat_id":chat_id,"user_id":target})
                        call(token,"sendMessage",{"chat_id":chat_id,"text":f"👢 تم طرد {name}"})
                    elif text=="كتم":
                        call(token,"restrictChatMember",{"chat_id":chat_id,"user_id":target,"permissions":{"can_send_messages":False}})
                        call(token,"sendMessage",{"chat_id":chat_id,"text":f"🔇 تم كتم {name}"})
                    elif text=="حظر":
                        call(token,"banChatMember",{"chat_id":chat_id,"user_id":target})
                        call(token,"sendMessage",{"chat_id":chat_id,"text":f"⛔ تم حظر {name}"})
        except: time.sleep(2)

def run_downloader_bot(token):
    offset=0
    while True:
        try:
            res = call(token,"getUpdates",{"offset":offset,"timeout":25})
            for upd in res.get("result",[]):
                offset=upd["update_id"]+1
                msg=upd.get("message",{})
                chat_id=msg.get("chat",{}).get("id")
                text=msg.get("text","")
                if not chat_id: continue
                if text=="/start":
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"📥 بوت التحميل الخارق الحقيقي ✅\n\n📱 تيك توك بدون علامة - شغال 100%\n📸 انستجرام - شغال بـ yt-dlp\n▶️ يوتيوب MP3/MP4\n🐦 تويتر\n👻 فيسبوك\n\nابعت الرابط الآن!"})
                elif "tiktok.com" in text:
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"📱 جاري تحميل تيك توك حقيقي بدون علامة..."})
                    info = download_tiktok_real(text)
                    if info["ok"]:
                        cap = f"✅ {info.get('title','')}\n👤 {info.get('author','')}"
                        if info.get("video_url"):
                            try:
                                call(token,"sendVideo",{"chat_id":chat_id,"video":info["video_url"],"caption":cap})
                            except:
                                call(token,"sendMessage",{"chat_id":chat_id,"text":f"{cap}\n🔗 {info['video_url']}"})
                elif "instagram.com" in text:
                    call(token,"sendMessage",{"chat_id
