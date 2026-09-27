import json, os, threading, time, urllib.request
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

# توكن مصنع ميمو الاصلي
FACTORY_TOKEN = os.getenv("TOKEN") or os.getenv("FACTORY_TOKEN") or "8835297704:AAHwG3vBZEMly31PH-WqBFLUXhebU_LMUEA"
DATA_FILE = "bots_pro.json"

# قناتك الرسمية
CHANNEL = "Memoofactory"
CHANNEL_URL = "https://t.me/Memoofactory"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Memo Factory - Source Memo - Pro - Running")
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

def is_admin(token, chat_id, user_id):
    r = call(token, "getChatMember", {"chat_id": chat_id, "user_id": user_id})
    return r.get("result", {}).get("status") in ["administrator", "creator"]

def dl_tiktok(url):
    try:
        if REQ:
            r = requests.post("https://www.tikwm.com/api/", data={"url": url}, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
            j = r.json()
            if j.get("code")==0:
                d=j.get("data",{})
                return {"ok":True,"url":d.get("play") or d.get("hdplay"),"title":d.get("title","TikTok"),"author":d.get("author",{}).get("nickname","")}
    except:
        pass
    return {"ok":False}

def dl_yt(url):
    try:
        if YTDLP:
            opts={'quiet':True,'no_warnings':True,'noplaylist':True,'format':'best'}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info=ydl.extract_info(url,download=False)
                return {"ok":True,"url":info.get("url"),"title":info.get("title","Video")}
    except:
        pass
    return {"ok":False}

def set_commands(token, btype):
    try:
        if btype=="protection":
            cmds=[
                {"command":"start","description":"✨ بداية البوت"},
                {"command":"help","description":"📚 قائمة الأوامر"},
                {"command":"ban","description":"حظر عضو"},
                {"command":"kick","description":"طرد عضو"},
                {"command":"mute","description":"كتم عضو"},
                {"command":"unmute","description":"فك الكتم"},
                {"command":"warn","description":"تحذير"},
                {"command":"pin","description":"تثبيت"},
                {"command":"lock","description":"قفل"},
                {"command":"unlock","description":"فتح"},
                {"command":"rules","description":"القوانين"},
                {"command":"settings","description":"الاعدادات"},
            ]
        elif btype=="downloader":
            cmds=[
                {"command":"start","description":"بداية بوت التحميل"},
                {"command":"help","description":"المساعدة"},
                {"command":"download","description":"تحميل رابط"},
                {"command":"tiktok","description":"تيك توك بدون علامة"},
                {"command":"youtube","description":"يوتيوب"},
                {"command":"instagram","description":"انستجرام"},
            ]
        else:
            cmds=[
                {"command":"start","description":"القائمة الرئيسية"},
                {"command":"help","description":"كل الأقسام"},
                {"command":"download","description":"تحميل"},
                {"command":"ban","description":"حظر"},
                {"command":"kick","description":"طرد"},
                {"command":"mute","description":"كتم"},
                {"command":"pin","description":"تثبيت"},
                {"command":"lock","description":"قفل"},
            ]
        call(token,"setMyCommands",{"commands":cmds})
    except:
        pass

# ==================== بوت الحماية - سورس ميمو - ستايل wHDBot ====================
def run_protection(token):
    set_commands(token,"protection")
    offset=0
    locks={}
    warns={}
    welcome_texts={}
    rules_texts={}
    print("Protection Memo started")
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
                        txt="📚 **أقسام أوامر الحماية - سورس ميمو**\n\nاختر القسم لعرض أوامره:"
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})
                    
                    elif data=="sec_prot":
                        txt="🛡️ **أوامر الحماية**\n\n• `/ban` - حظر العضو بالرد\n• `/kick` - طرد العضو بالرد\n• `/mute` - كتم العضو بالرد\n• `/unmute` - فك الكتم\n• `/warn` - تحذير (3 تحذيرات = حظر)\n\n💬 بالعربي: حظر - طرد - كتم - فك الكتم"
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb})
                    
                    elif data=="sec_lock":
                        txt="🔒 **أوامر القفل - سورس ميمو**\n\n• `/lock links` - قفل الروابط\n• `/lock photos` - قفل الصور\n• `/lock videos` - قفل الفيديو\n• `/lock stickers` - قفل الملصقات\n• `/lock all` - قفل الكل\n\n• `/unlock links` - فتح الروابط\n• `/unlock all` - فتح الكل\n• `/locks` - عرض الأقفال النشطة\n\n💬 بالعربي: قفل الروابط - فتح الروابط"
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb})
                    
                    elif data=="sec_info":
                        txt="ℹ️ **أوامر المعلومات**\n\n• `/id` - معرفك ومعرف الشات\n• `/info` - معلومات العضو بالرد\n• `/whoami` - معلوماتك\n• `/group` - معلومات المجموعة\n• `/locks` - حالة الأقفال"
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb})
                    
                    elif data=="sec_admin":
                        txt="⚙️ **أوامر الإدارة**\n\n• `/pin` - تثبيت رسالة بالرد\n• `/unpin` - إلغاء التثبيت\n• `/promote` - رفع أدمن\n• `/demote` - تنزيل أدمن\n• `/setrules` - تعيين القوانين\n• `/setwelcome` - تعيين الترحيب\n• `/settings` - إعدادات المجموعة"
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb})
                    
                    elif data=="show_rules":
                        rules=rules_texts.get(str(chat_id),"لا توجد قوانين معينة حاليا")
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":f"📜 **قوانين المجموعة**\n\n{rules}","reply_markup":kb})
                    
                    elif data=="show_welcome":
                        wel=welcome_texts.get(str(chat_id),"أهلا وسهلا")
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"help_main"}]]}
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":f"👋 **رسالة الترحيب**\n\n{wel}","reply_markup":kb})
                    
                    elif data=="back_start":
                        me=call(token,"getMe").get("result",{})
                        username=me.get("username","")
                        kb={"inline_keyboard":[
                            [{"text":"➕ أضفني لمجموعتك","url":f"https://t.me/{username}?startgroup=new"}],
                            [{"text":"📚 أوامري","callback_data":"help_main"},{"text":"⚙️ الإعدادات","callback_data":"sec_admin"}],
                            [{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]
                        ]}
                        txt=f"✨ **بوت الحماية - سورس ميمو**\n\n🤖 @{username}\n🛡️ حماية احترافية للجروبات\n⭐️ خليك مميز ونصب بوت حماية باسمك\n\n👇 اختر من القائمة:"
                        call(token,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})
                    continue

                msg=upd.get("message",{})
                chat=msg.get("chat",{})
                chat_id=chat.get("id")
                chat_type=chat.get("type","")
                text=msg.get("text","") or msg.get("caption","")
                from_id=msg.get("from",{}).get("id")
                reply=msg.get("reply_to_message")
                new_member=msg.get("new_chat_member")
                if not chat_id:
                    continue

                # ترحيب بالأعضاء الجدد
                if new_member and chat_type!="private":
                    wel=welcome_texts.get(str(chat_id))
                    if wel:
                        call(token,"sendMessage",{"chat_id":chat_id,"text":wel})

                # فحص الأقفال
                if chat_type!="private":
                    cfg=locks.get(str(chat_id),{})
                    if from_id and not is_admin(token,chat_id,from_id):
                        if cfg.get("links") and ("http" in text or "t.me/" in text or "www." in text):
                            try:
                                call(token,"deleteMessage",{"chat_id":chat_id,"message_id":msg.get("message_id")})
                            except:
                                pass
                            continue
                        if cfg.get("photos") and msg.get("photo"):
                            try:
                                call(token,"deleteMessage",{"chat_id":chat_id,"message_id":msg.get("message_id")})
                            except:
                                pass
                            continue
                        if cfg.get("videos") and (msg.get("video") or msg.get("video_note")):
                            try:
                                call(token,"deleteMessage",{"chat_id":chat_id,"message_id":msg.get("message_id")})
                            except:
                                pass
                            continue
                        if cfg.get("stickers") and msg.get("sticker"):
                            try:
                                call(token,"deleteMessage",{"chat_id":chat_id,"message_id":msg.get("message_id")})
                            except:
                                pass
                            continue

                if text in ["/start","/start@"+call(token,"getMe").get("result",{}).get("username","")]:
                    me=call(token,"getMe").get("result",{})
                    username=me.get("username","")
                    kb={"inline_keyboard":[
                        [{"text":"➕ أضفني لمجموعتك","url":f"https://t.me/{username}?startgroup=new"}],
                        [{"text":"📚 أوامري","callback_data":"help_main"},{"text":"📜 القوانين","callback_data":"show_rules"}],
                        [{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]
                    ]}
                    txt=f"✨ **أهلا بك في بوت الحماية**\n\n🤖 المعرف: @{username}\n🛡️ **سورس ميمو**\n⭐️ خليك مميز ونصب بوت حماية باسمك\n\n🔹 حماية متكاملة\n🔹 نظام قفل احترافي\n🔹 طرد / حظر / كتم بالرد\n\n👇 استخدم الأزرار:"
                    call(token,"sendMessage",{"chat_id":chat_id,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})

                if text in ["/help","مساعدة","الاوامر"]:
                    kb={"inline_keyboard":[
                        [{"text":"🛡️ الحماية","callback_data":"sec_prot"},{"text":"🔒 القفل","callback_data":"sec_lock"}],
                        [{"text":"ℹ️ المعلومات","callback_data":"sec_info"},{"text":"⚙️ الإدارة","callback_data":"sec_admin"}]
                    ]}
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"📚 **أقسام الأوامر - سورس ميمو**\n\nاختر القسم:","reply_markup":kb,"parse_mode":"Markdown"})

                if text in ["تفعيل","تفعيل المجموعة","/activate","فعل"]:
                    if chat_type=="private":
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"📍 أضفني مجموعة وارفعني أدمن واكتب تفعيل"})
                    else:
                        if not is_admin(token,chat_id,from_id):
                            call(token,"sendMessage",{"chat_id":chat_id,"text":"❌ يجب أن تكون أدمن"})
                        else:
                            kb={"inline_keyboard":[[{"text":"📚 أوامري","callback_data":"help_main"}]]}
                            call(token,"sendMessage",{"chat_id":chat_id,"text":f"✅ **تم تفعيل المجموعة**\n\n📛 {chat.get('title')}\n🛡️ البوت الآن يحمي مجموعتك\n\nاكتب /help","reply_markup":kb,"parse_mode":"Markdown"})

                if text in ["/id","ايدي","الايدي"]:
                    txt=f"🆔 **معرفاتك**\n\n👤 ايديك: `{from_id}`\n💬 ايدي الشات: `{chat_id}`"
                    if reply:
                        txt+=f"\n👤 ايدي المردود عليه: `{reply['from']['id']}`"
                    call(token,"sendMessage",{"chat_id":chat_id,"text":txt,"parse_mode":"Markdown"})

                if text in ["/rules","القوانين","قوانين"]:
                    rules=rules_texts.get(str(chat_id),"لا توجد قوانين حاليا\n\nالمشرف يمكنه وضعها بـ /setrules النص")
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"📜 **قوانين المجموعة**\n\n{rules}"})

                if text.startswith("/setrules "):
                    if not is_admin(token,chat_id,from_id):
                        continue
                    rules_texts[str(chat_id)]=text.replace("/setrules ","")
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"✅ تم حفظ القوانين"})

                if text.startswith("/setwelcome "):
                    if not is_admin(token,chat_id,from_id):
                        continue
                    welcome_texts[str(chat_id)]=text.replace("/setwelcome ","")
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"✅ تم حفظ رسالة الترحيب"})

                if text in ["طرد","/kick"] and reply:
                    if not is_admin(token,chat_id,from_id): continue
                    target=reply["from"]["id"]
                    call(token,"banChatMember",{"chat_id":chat_id,"user_id":target})
                    call(token,"unbanChatMember",{"chat_id":chat_id,"user_id":target})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"👢 تم طرد {reply['from']['first_name']}"})

                if text in ["حظر","/ban"] and reply:
                    if not is_admin(token,chat_id,from_id): continue
                    target=reply["from"]["id"]
                    call(token,"banChatMember",{"chat_id":chat_id,"user_id":target})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"🔨 تم حظر {reply['from']['first_name']}"})

                if text in ["كتم","/mute"] and reply:
                    if not is_admin(token,chat_id,from_id): continue
                    target=reply["from"]["id"]
                    call(token,"restrictChatMember",{"chat_id":chat_id,"user_id":target,"permissions":{"can_send_messages":False}})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"🔇 تم كتم {reply['from']['first_name']}"})

                if text in ["/unmute","فك الكتم","الغاء الكتم"] and reply:
                    if not is_admin(token,chat_id,from_id): continue
                    target=reply["from"]["id"]
                    call(token,"restrictChatMember",{"chat_id":chat_id,"user_id":target,"permissions":{"can_send_messages":True,"can_send_media_messages":True,"can_send_other_messages":True,"can_add_web_page_previews":True}})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"🔊 تم فك كتم {reply['from']['first_name']}"})

                if text in ["/unban","فك الحظر","الغاء الحظر"] and reply:
                    if not is_admin(token,chat_id,from_id): continue
                    target=reply["from"]["id"]
                    call(token,"unbanChatMember",{"chat_id":chat_id,"user_id":target})
                    call(token,"sendMessage",{"chat_id":chat_id,"text":f"✅ تم فك حظر {reply['from']['first_name']}"})

                if text in ["تثبيت","/pin"] and reply:
                    if not is_admin(token,chat_id,from_id): continue
                    try:
                        call(token,"pinChatMessage",{"chat_id":chat_id,"message_id":reply["message_id"]})
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"📌 تم التثبيت"})
                    except:
                        pass

                if text in ["/unpin","الغاء التثبيت","الغاء تثبيت"]:
                    if not is_admin(token,chat_id,from_id): continue
                    try:
                        call(token,"unpinChatMessage",{"chat_id":chat_id})
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"📍 تم إلغاء التثبيت"})
                    except:
                        pass

                if text.startswith("/warn") or text=="تحذير":
                    if not is_admin(token,chat_id,from_id): continue
                    if reply:
                        target=reply["from"]["id"]
                        key=f"{chat_id}_{target}"
                        warns[key]=warns.get(key,0)+1
                        c=warns[key]
                        if c>=3:
                            call(token,"banChatMember",{"chat_id":chat_id,"user_id":target})
                            call(token,"sendMessage",{"chat_id":chat_id,"text":f"🔨 تم حظر {reply['from']['first_name']} - 3 تحذيرات"})
                            warns[key]=0
                        else:
                            call(token,"sendMessage",{"chat_id":chat_id,"text":f"⚠️ تحذير {c}/3 لـ {reply['from']['first_name']}"})

                if text.startswith("/lock") or text.startswith("قفل "):
                    if not is_admin(token,chat_id,from_id): continue
                    cfg=locks.get(str(chat_id),{})
                    what=text.lower()
                    if "link" in what or "الروابط" in what or "الرابط" in what:
                        cfg["links"]=True
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔒 تم قفل الروابط"})
                    if "photo" in what or "الصور" in what:
                        cfg["photos"]=True
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔒 تم قفل الصور"})
                    if "video" in what or "الفيديو" in what:
                        cfg["videos"]=True
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔒 تم قفل الفيديو"})
                    if "sticker" in what or "الملصقات" in what:
                        cfg["stickers"]=True
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔒 تم قفل الملصقات"})
                    if "all" in what or "الكل" in what:
                        cfg={"links":True,"photos":True,"videos":True,"stickers":True}
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔒 تم قفل الكل"})
                    locks[str(chat_id)]=cfg

                if text.startswith("/unlock") or text.startswith("فتح "):
                    if not is_admin(token,chat_id,from_id): continue
                    cfg=locks.get(str(chat_id),{})
                    what=text.lower()
                    if "link" in what or "الروابط" in what:
                        cfg["links"]=False
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔓 تم فتح الروابط"})
                    if "photo" in what or "الصور" in what:
                        cfg["photos"]=False
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔓 تم فتح الصور"})
                    if "all" in what or "الكل" in what:
                        cfg={}
                        call(token,"sendMessage",{"chat_id":chat_id,"text":"🔓 تم فتح الكل"})
                    locks[str(chat_id)]=cfg

                if text in ["/locks","الاقفال","حالة الاقفال"]:
                    cfg=locks.get(str(chat_id),{})
                    txt="🔒 **حالة الأقفال**\n\n"
                    txt+=f"🔗 الروابط: {'🔒 مقفول' if cfg.get('links') else '🔓 مفتوح'}\n"
                    txt+=f"🖼️ الصور: {'🔒 مقفول' if cfg.get('photos') else '🔓 مفتوح'}\n"
                    txt+=f"🎥 الفيديو: {'🔒 مقفول' if cfg.get('videos') else '🔓 مفتوح'}\n"
                    txt+=f"😀 الملصقات: {'🔒 مقفول' if cfg.get('stickers') else '🔓 مفتوح'}"
                    call(token,"sendMessage",{"chat_id":chat_id,"text":txt})

        except Exception as e:
            print(e)
            time.sleep(2)

def run_downloader(token):
    set_commands(token,"downloader")
    offset=0
    while True:
        try:
            res=call(token,"getUpdates",{"offset":offset,"timeout":25})
            for upd in res.get("result",[]):
                offset=upd["update_id"]+1
                msg=upd.get("message",{})
                chat_id=msg.get("chat",{}).get("id")
                text=msg.get("text","")
                if not chat_id:
                    continue
                if text=="/start":
                    me=call(token,"getMe").get("result",{})
                    kb={"inline_keyboard":[
                        [{"text":"🎵 تيك توك بدون علامة","callback_data":"dl_tiktok"},{"text":"▶️ يوتيوب","callback_data":"dl_youtube"}],
                        [{"text":"📸 انستا","callback_data":"dl_insta"},{"text":"🔵 فيسبوك","callback_data":"dl_fb"}],
                        [{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]
                    ]}
                    txt=f"✨ **بوت التحميل - سورس ميمو**\n\n🤖 @{me.get('username','')}\n📥 تحميل حقيقي بدون علامة مائية\n\n👇 أرسل رابط الآن:"
                    call(token,"sendMessage",{"chat_id":chat_id,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})
                if text.startswith("/download "):
                    text=text.replace("/download ","").strip()
                if "tiktok.com" in text:
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"⏳ جاري تحميل تيك توك بدون علامة..."})
                    info=dl_tiktok(text)
                    if info["ok"]:
                        try:
                            call(token,"sendVideo",{"chat_id":chat_id,"video":info["url"],"caption":info.get("title","")})
                        except:
                            call(token,"sendMessage",{"chat_id":chat_id,"text":info["url"]})
                if ("youtube.com" in text or "youtu.be" in text or "instagram.com" in text or "facebook.com" in text or "fb.watch" in text) and "tiktok.com" not in text:
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"⏳ جاري التحميل..."})
                    info=dl_yt(text)
                    if info["ok"]:
                        try:
                            call(token,"sendVideo",{"chat_id":chat_id,"video":info["url"],"caption":info.get("title","")})
                        except:
                            call(token,"sendMessage",{"chat_id":chat_id,"text":info["url"]})
        except Exception as e:
            print(e)
            time.sleep(2)

def run_allinone(token):
    set_commands(token,"allinone")
    offset=0
    while True:
        try:
            res=call(token,"getUpdates",{"offset":offset,"timeout":25})
            for upd in res.get("result",[]):
                offset=upd["update_id"]+1
                msg=upd.get("message",{})
                chat_id=msg.get("chat",{}).get("id")
                text=msg.get("text","") or ""
                if not chat_id:
                    continue
                if text=="/start":
                    me=call(token,"getMe").get("result",{})
                    kb={"inline_keyboard":[
                        [{"text":"🛡️ حماية","callback_data":"help_main"},{"text":"📥 تحميل","callback_data":"help_dl"}],
                        [{"text":"📚 كل الأوامر","callback_data":"help_main"}],
                        [{"text":"📢 سورس ميمو","url":CHANNEL_URL}]
                    ]}
                    txt=f"✨ **البوت الشامل - سورس ميمو**\n\n🤖 @{me.get('username','')}\n🚀 حماية + تحميل\n\n👇 اختر القسم:"
                    call(token,"sendMessage",{"chat_id":chat_id,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})
                if "tiktok.com" in text:
                    call(token,"sendMessage",{"chat_id":chat_id,"text":"⏳ بحمل تيك توك..."})
                    info=dl_tiktok(text)
                    if info["ok"]:
                        try:
                            call(token,"sendVideo",{"chat_id":chat_id,"video":info["url"],"caption":info.get("title","")})
                        except:
                            call(token,"sendMessage",{"chat_id":chat_id,"text":info["url"]})
        except Exception as e:
            print(e)
            time.sleep(2)

RUNNERS={"protection":run_protection,"downloader":run_downloader,"allinone":run_allinone,"music":run_downloader,"movies":run_downloader}
pending={}

def factory_loop():
    bots=load_bots()
    for username,info in bots.items():
        token=info.get("token")
        btype=info.get("type","allinone")
        threading.Thread(target=RUNNERS.get(btype,run_allinone),args=(token,),daemon=True).start()

    offset=0
    print("Memo Factory - Source Memo - ExpProx Style - Ready")
    while True:
        try:
            res=call(FACTORY_TOKEN,"getUpdates",{"offset":offset,"timeout":25})
            for upd in res.get("result",[]):
                offset=upd["update_id"]+1
                if "callback_query" in upd:
                    cq=upd["callback_query"]
                    chat_id=cq["message"]["chat"]["id"]
                    data=cq["data"]
                    mid=cq["message"]["message_id"]
                    call(FACTORY_TOKEN,"answerCallbackQuery",{"callback_query_id":cq["id"]})

                    if data=="make_bot":
                        txt="🔑 **أرسل توكن البوت**\n\n📍 روح @BotFather\n📍 اكتب /newbot\n📍 اختر اسم وشكل\n📍 انسخ التوكن وارسله هنا\n\nمثال:\n`123456789:AAH...`"
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":txt,"parse_mode":"Markdown"})

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
                        bots=load_bots()
                        bots[bot_user]={"token":token,"type":btype,"name":me["result"].get("first_name","")}
                        save_bots(bots)
                        threading.Thread(target=RUNNERS.get(btype,run_allinone),args=(token,),daemon=True).start()
                        del pending[key]
                        kb={"inline_keyboard":[
                            [{"text":f"🚀 اذهب للبوت @{bot_user}","url":f"https://t.me/{bot_user}"}],
                            [{"text":"➕ صنع بوت آخر","callback_data":"make_bot"}],
                            [{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]
                        ]}
                        txt=f"✅ **تم صنع البوت بنجاح - سورس ميمو**\n\n🤖 المعرف: @{bot_user}\n📦 النوع: {btype}\n⭐️ خليك مميز ونصب بوت حماية باسمك\n\n🔹 قائمة أوامر مقسمة في خانات\n🔹 أزرار احترافية\n🔹 يمكنك رفع نسخة احتياطية لاسترجاع الإحصائيات\n\nجرب /start في البوت الجديد"
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})

                    elif data=="my_bots":
                        bots=load_bots()
                        if not bots:
                            call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":"📭 لا يوجد بوتات مصنوعة حاليا"})
                        else:
                            txt="📊 **بوتاتك المصنوعة - سورس ميمو**\n\n"
                            for u,i in bots.items():
                                txt+=f"🤖 @{u} - {i.get('type')}\n"
                            call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":txt})

                    elif data=="factory_info":
                        txt=f"ℹ️ **معلومات مصنع ميمو**\n\n🏭 مصنع ميمو - سورس ميمو\n📢 القناة: @{CHANNEL}\n👨‍💻 المطور: Ahmed Mokhtar\n\n🔹 مصنع بوتات حماية احترافي\n🔹 مثل @wHDBot\n🔹 يمكنك دائما رفع نسخة احتياطية\n\n⭐️ خليك مميز ونصب بوت حماية باسمك"
                        kb={"inline_keyboard":[[{"text":"🔙 رجوع","callback_data":"back_main"}]]}
                        call(FACTORY_TOKEN,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})

                    elif data=="back_main":
                        kb={"inline_keyboard":[
                            [{"text":"🤖 صنع بوت حماية","callback_data":"make_bot"}],
                            [{"text":"📊 بوتاتي","callback_data":"my_bots"},{"text":"ℹ️ معلومات","callback_data":"factory_info"}],
                            [{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]
                        ]}
                        txt="⭐️ **خليك مميز ونصب بوت حماية باسمك** ⭐️\n\n✨ **مصنع ميمو - سورس ميمو**\n\n🛡️ صنع بوتات حماية احترافية\n📥 يمكنك دائما رفع أي نسخة احتياطية لاسترجاع إحصائيات البوت الخاص بك\n\n👇 اختر:"
                        call(FACTORY_TOKEN,"editMessageText",{"chat_id":chat_id,"message_id":mid,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})
                    continue

                msg=upd.get("message",{})
                chat_id=msg.get("chat",{}).get("id")
                text=msg.get("text","")
                if not chat_id:
                    continue

                if text=="/start":
                    kb={"inline_keyboard":[
                        [{"text":"🤖 صنع بوت حماية","callback_data":"make_bot"}],
                        [{"text":"📊 بوتاتي","callback_data":"my_bots"},{"text":"ℹ️ معلومات","callback_data":"factory_info"}],
                        [{"text":"📢 قناة سورس ميمو","url":CHANNEL_URL}]
                    ]}
                    txt="⭐️ **خليك مميز ونصب بوت حماية باسمك** ⭐️\n\n✨ **مصنع ميمو - سورس ميمو**\n\n🛡️ مصنع بوتات حماية احترافي\n💾 يمكنك دائما رفع أي نسخة احتياطية لاسترجاع إحصائيات البوت الخاص بك\n\n📦 الأنواع:\n• حماية جروبات متكامل\n• تحميل ميديا حقيقي\n• شامل برو\n\n👇 اختر:"
                    call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})

                if text and len(text)>20 and ":" in text and " " not in text:
                    me=call(text,"getMe")
                    if me.get("ok"):
                        pending[str(chat_id)]=text
                        kb={"inline_keyboard":[
                            [{"text":"🛡️ حماية جروبات - سورس ميمو","callback_data":"type_protection"}],
                            [{"text":"📥 تحميل ميديا حقيقي","callback_data":"type_downloader"}],
                            [{"text":"🚀 شامل برو - حماية + تحميل","callback_data":"type_allinone"}]
                        ]}
                        txt=f"✅ **توكن @{me['result']['username']} صحيح**\n\nاختر نوع البوت - ستايل @wHDBot:"
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":txt,"reply_markup":kb,"parse_mode":"Markdown"})
                    else:
                        call(FACTORY_TOKEN,"sendMessage",{"chat_id":chat_id,"text":"❌ التوكن غلط - تأكد من @BotFather"})
        except Exception as e:
            print(e)
            time.sleep(2)

factory_loop()
