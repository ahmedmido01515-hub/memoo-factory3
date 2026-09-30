import asyncio, time, re
from collections import defaultdict
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

RUNNING_BOTS = {}
GROUP_SETTINGS = defaultdict(lambda: {"link": True, "spam": True, "flood": True, "sticker": False, "photo": False, "forward": True, "profanity": True})
USER_FLOOD = defaultdict(list)

def get_all_bots():
    return RUNNING_BOTS

def main_keyboard(chat_id):
    s = GROUP_SETTINGS[chat_id]
    def txt(name, on): return f"{'🔒' if on else '🔓'} {name}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=txt("الروابط", s["link"]), callback_data="toggle_link"),
         InlineKeyboardButton(text=txt("التوجيه", s["forward"]), callback_data="toggle_forward")],
        [InlineKeyboardButton(text=txt("التكرار", s["flood"]), callback_data="toggle_flood"),
         InlineKeyboardButton(text=txt("الكلايش", s["spam"]), callback_data="toggle_spam")],
        [InlineKeyboardButton(text=txt("الملصقات", s["sticker"]), callback_data="toggle_sticker"),
         InlineKeyboardButton(text=txt("الصور", s["photo"]), callback_data="toggle_photo")],
        [InlineKeyboardButton(text="📜 الاوامر", callback_data="show_help"),
         InlineKeyboardButton(text="⚙️ الاعدادات", callback_data="show_settings")],
        [InlineKeyboardButton(text="📢 قناة السورس", url="https://t.me/Memoofactory")],
    ])

def help_text():
    return """
🤖 **بوت حماية سورس ميمو - قائمة الاوامر الاحترافية**

**🔹 اوامر القفل والفتح:**
/قفل الروابط - /فتح الروابط
/قفل التكرار - /فتح التكرار
/قفل الكلايش - /فتح الكلايش
/قفل الملصقات - /فتح الملصقات
/قفل الصور - /فتح الصور
/قفل التوجيه - /فتح التوجيه

**🔹 اوامر الادارة:**
/طرد - رد على الشخص
/كتم - رد على الشخص
/الغاء_كتم - رد على الشخص
/تثبيت - رد على الرسالة
/الاعدادات - لوحة التحكم

**🔹 اوامر عامة:**
/start - تشغيل البوت
/help - هذه القائمة

المصنع: @memoo_factory_bot
المطور: @mernaqueen
"""

def get_protection_dispatcher(bot_type="free"):
    dp = Dispatcher()

    @dp.message(Command("start", "help", "الاوامر"))
    async def start_handler(message: Message):
        await message.answer(
            f"🛡️ **بوت حماية سورس ميمو**\nالنوع: {bot_type}\n\nاختر من لوحة التحكم:",
            reply_markup=main_keyboard(message.chat.id),
            parse_mode="Markdown"
        )

    @dp.message(Command("الاعدادات", "settings"))
    async def settings_handler(message: Message):
        await message.answer("⚙️ **لوحة تحكم الحماية**", reply_markup=main_keyboard(message.chat.id))

    # اوامر نصية
    @dp.message(F.text.startswith("/قفل"))
    async def lock_cmd(message: Message):
        if not await is_admin(message): return
        text = message.text
        chat = message.chat.id
        if "الروابط" in text: GROUP_SETTINGS[chat]["link"] = True
        if "التكرار" in text: GROUP_SETTINGS[chat]["flood"] = True
        if "الكلايش" in text: GROUP_SETTINGS[chat]["spam"] = True
        if "الملصقات" in text: GROUP_SETTINGS[chat]["sticker"] = True
        if "الصور" in text: GROUP_SETTINGS[chat]["photo"] = True
        if "التوجيه" in text: GROUP_SETTINGS[chat]["forward"] = True
        await message.reply(f"🔒 تم القفل: {text}", reply_markup=main_keyboard(chat))

    @dp.message(F.text.startswith("/فتح"))
    async def unlock_cmd(message: Message):
        if not await is_admin(message): return
        text = message.text
        chat = message.chat.id
        if "الروابط" in text: GROUP_SETTINGS[chat]["link"] = False
        if "التكرار" in text: GROUP_SETTINGS[chat]["flood"] = False
        if "الكلايش" in text: GROUP_SETTINGS[chat]["spam"] = False
        if "الملصقات" in text: GROUP_SETTINGS[chat]["sticker"] = False
        if "الصور" in text: GROUP_SETTINGS[chat]["photo"] = False
        if "التوجيه" in text: GROUP_SETTINGS[chat]["forward"] = False
        await message.reply(f"🔓 تم الفتح: {text}", reply_markup=main_keyboard(chat))

    @dp.message(Command("طرد"))
    async def ban_cmd(message: Message):
        if not await is_admin(message): return
        if message.reply_to_message:
            try:
                await message.chat.ban_member(message.reply_to_message.from_user.id)
                await message.reply("✅ تم طرد العضو")
            except:
                await message.reply("❌ ارفعني ادمن اولا")

    @dp.message(Command("كتم"))
    async def mute_cmd(message: Message):
        if not await is_admin(message): return
        if message.reply_to_message:
            try:
                await message.chat.restrict_member(message.reply_to_message.from_user.id, permissions={"can_send_messages": False})
                await message.reply("🔇 تم كتم العضو")
            except:
                await message.reply("❌ ارفعني ادمن")

    # ازرار لوحة التحكم
    @dp.callback_query(F.data.startswith("toggle_"))
    async def toggle_cb(callback: CallbackQuery):
        if not await is_admin_cb(callback):
            await callback.answer("للمشرفين فقط", show_alert=True)
            return
        key = callback.data.replace("toggle_", "")
        GROUP_SETTINGS[callback.message.chat.id][key] = not GROUP_SETTINGS[callback.message.chat.id][key]
        await callback.message.edit_reply_markup(reply_markup=main_keyboard(callback.message.chat.id))
        await callback.answer(f"{'تم القفل' if GROUP_SETTINGS[callback.message.chat.id][key] else 'تم الفتح'}")

    @dp.callback_query(F.data == "show_help")
    async def help_cb(callback: CallbackQuery):
        await callback.message.answer(help_text(), parse_mode="Markdown")
        await callback.answer()

    @dp.callback_query(F.data == "show_settings")
    async def settings_cb(callback: CallbackQuery):
        await callback.message.edit_text("⚙️ **اعدادات الحماية**", reply_markup=main_keyboard(callback.message.chat.id), parse_mode="Markdown")
        await callback.answer()

    # نظام الحماية الفعلي
    @dp.message(F.text)
    async def protection_filter(message: Message):
        if await is_admin(message): return
        chat = message.chat.id
        s = GROUP_SETTINGS[chat]
        text = message.text or ""

        # روابط
        if s["link"] and re.search(r"https?://|t\.me/|telegram\.me", text):
            try: await message.delete(); return
            except: pass

        # توجيه
        if s["forward"] and message.forward_from:
            try: await message.delete(); return
            except: pass

        # كلايش - رسائل طويلة
        if s["spam"] and len(text) > 300:
            try: await message.delete(); return
            except: pass

        # تكرار - فلود
        if s["flood"]:
            uid = message.from_user.id
            now = time.time()
            USER_FLOOD[uid] = [t for t in USER_FLOOD[uid] if now - t < 5]
            USER_FLOOD[uid].append(now)
            if len(USER_FLOOD[uid]) > 4:
                try:
                    await message.delete()
                    await message.chat.restrict_member(uid, permissions={"can_send_messages": False}, until_date=int(now+60))
                    await message.answer(f"🚫 تم كتم {message.from_user.mention_html()} بسبب التكرار", parse_mode="HTML")
                except: pass
                return

    @dp.message(F.sticker)
    async def sticker_filter(message: Message):
        if GROUP_SETTINGS[message.chat.id]["sticker"] and not await is_admin(message):
            try: await message.delete()
            except: pass

    @dp.message(F.photo)
    async def photo_filter(message: Message):
        if GROUP_SETTINGS[message.chat.id]["photo"] and not await is_admin(message):
            try: await message.delete()
            except: pass

    return dp

async def is_admin(message: Message):
    try:
        member = await message.chat.get_member(message.from_user.id)
        return member.status in ["administrator", "creator"]
    except: return True

async def is_admin_cb(callback: CallbackQuery):
    try:
        member = await callback.message.chat.get_member(callback.from_user.id)
        return member.status in ["administrator", "creator"]
    except: return False

async def create_and_run_protection_bot(bot_token: str, bot_type: str="free"):
    if bot_token in RUNNING_BOTS:
        return False, "البوت شغال بالفعل"
    try:
        tmp = Bot(token=bot_token)
        me = await tmp.get_me()
        # قايمة الاوامر اللي بتظهر في المربعات
        await tmp.set_my_commands([
            {"command": "start", "description": "تشغيل البوت"},
            {"command": "help", "description": "قائمة الاوامر"},
            {"command": "الاعدادات", "description": "لوحة التحكم"},
            {"command": "قفل_الروابط", "description": "قفل الروابط"},
            {"command": "فتح_الروابط", "description": "فتح الروابط"},
            {"command": "قفل_التكرار", "description": "قفل التكرار"},
            {"command": "طرد", "description": "طرد بالرد"},
            {"command": "كتم", "description": "كتم بالرد"},
        ])
        await tmp.session.close()

        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode="HTML"))
        dp = get_protection_dispatcher(bot_type)
        task = asyncio.create_task(dp.start_polling(bot))
        RUNNING_BOTS[bot_token] = {"task": task, "username": me.username, "bot": bot}
        return True, f"@{me.username}"
    except Exception as e:
        return False, str(e)
