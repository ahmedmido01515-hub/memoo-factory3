# سورس ميمو - Source Memo - النسخة النهائية الكاملة V4 الدائمة
# قناة السورس: https://t.me/Memoofactory
# مطور السورس: @MernaQueen
# معرف المصنع: @memoo_factory_bot
# الاصدار: دائم 24/7 + نظام مدفوع يدوي

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ملفات السورس
import config
from database import db
from bot_runner import create_and_run_protection_bot, get_all_bots
from keep_alive import keep_alive

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# حالات انتظار التوكن
class MakeBot(StatesGroup):
    waiting_token = State()

# كيبورد المصنع الرئيسي
def factory_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏭 صنع بوت حماية مجاني", callback_data="make_free")],
        [InlineKeyboardButton(text="💎 صنع بوت حماية مدفوع", callback_data="make_paid")],
        [InlineKeyboardButton(text="📊 احصائيات المصنع", callback_data="stats")],
        [InlineKeyboardButton(text="📢 قناة سورس ميمو", url=config.CHANNEL_LINK)],
        [InlineKeyboardButton(text="👨‍💻 مطور السورس", url=f"https://t.me/{config.DEVELOPER.replace('@','')}")]
    ])

@dp.message(CommandStart())
async def start_handler(message: Message):
    count = len(get_all_bots())
    text = f"""
أهلا يا باشا في <b>{config.SOURCE_NAME}</b> 👋

أقوى مصنع بوتات حماية في تليجرام
المصنع شغال دائم 24/7 ⚡️

🤖 البوتات اللي شغالة حاليا: {count} بوت

🔹 <b>المجاني:</b> حماية كاملة وسريعة
🔹 <b>المدفوع:</b> حماية ضد التفليش + مميزات VIP

اختر نوع البوت من تحت 👇

المصنع: {config.FACTORY_BOT}
المطور: {config.DEVELOPER}
"""
    await message.answer(text, reply_markup=factory_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "make_free")
async def ask_free_token(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MakeBot.waiting_token)
    await state.update_data(bot_type="free")
    await callback.message.answer(
        "تمام اخترت البوت <b>المجاني</b> ✅\n\n"
        "روح لـ @BotFather اعمل بوت جديد وهات التوكن بتاعه والصقه هنا فورا 👇\n\n"
        "مثال: <code>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</code>",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "make_paid")
async def make_paid_bot(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💻 كلم المطور للدفع @mernaqueen", url="https://t.me/mernaqueen")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="back_home")]
    ])

    text = f"""
💎 <b>نظام البوت المدفوع - سورس ميمو</b>

مميزات المدفوع:
✅ طرد تلقائي للسبام والتفليش
✅ منع التكرار والروابط الاباحية
✅ نظام رتب (ادمن - مميز)
✅ ترحيب بالصور + لوحة تحكم

<b>السعر: {config.PAID_BOT_PRICE} جنيه</b>

👇 <b>طريقة التفعيل:</b>
1- دوس على الزرار اللي تحت وكلم المطور @mernaqueen
2- هيبعتلك رقم التحويل (فودافون كاش)
3- بعد التحويل ابعتله توكن بوتك
4- هيفعلهولك فورا بشكل دائم 24/7

المطور: {config.DEVELOPER}
القناة: {config.CHANNEL_LINK}
"""
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "back_home
