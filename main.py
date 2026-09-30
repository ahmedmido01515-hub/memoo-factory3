import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import config
from database import db

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# زرار البداية - واجهة المصنع
def factory_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏭 صنع بوت حماية مجاني", callback_data="make_free")],
        [InlineKeyboardButton(text="💎 صنع بوت حماية مدفوع - مميز", callback_data="make_paid")],
        [InlineKeyboardButton(text="🤖 بوتاتي المصنوعة", callback_data="my_bots")],
        [InlineKeyboardButton(text="📢 قناة السورس", url=config.CHANNEL_LINK)],
        [InlineKeyboardButton(text="👨‍💻 مطور السورس", url=f"https://t.me/{config.DEVELOPER.replace('@','')}")]
    ])

@dp.message(CommandStart())
async def start_handler(message: Message):
    # رسالة الترحيب بالمصري
    text = f"""
أهلا يا باشا في **{config.SOURCE_NAME}** 👋

أقوى مصنع بوتات حماية في تليجرام
تقدر تصنع بوت حماية لقروبك في ثانية

🔹 المجاني: حماية كاملة و سريعة
🔹 المدفوع: حماية ضد التفليش + مميزات جبارة

المصنع الرسمي: {config.FACTORY_BOT}
المطور: {config.DEVELOPER}
"""
    await message.answer(text, reply_markup=factory_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "make_free")
async def make_free_bot(callback):
    await callback.message.answer("تمام، ابعتلي دلوقتي توكن البوت اللي جبته من @BotFather عشان اصنعهولك مجاني 👇\n\nمثال: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    # هنا المنطق بياخد التوكن ويعمل نسخة من سورس الحماية ويشغله
    # الكود الكامل للتشغيل التلقائي موجود في ملف bot_runner.py

@dp.callback_query(F.data == "make_paid")
async def make_paid_bot(callback):
    text = f"""
💎 **البوت المدفوع من سورس ميمو**

مميزاته:
✅ طرد تلقائي للسبام والتفليش
✅ منع التكرار والروابط والصور الاباحية
✅ نظام رتب (ادمن - مميز - عضو)
✅ ترحيب بالصور
✅ لوحة تحكم

السعر: {config.PAID_BOT_PRICE} جنيه
للدفع كلم المطور: {config.DEVELOPER}

بعد الدفع ابعت توكن بوتك هنا وهيتفتحلك المدفوع فورا.
"""
    await callback.message.answer(text)

async def main():
    await db.create_tables() # بنجهز قاعدة البيانات
    print(f"مصنع {config.SOURCE_NAME} اشتغل بنجاح يا ميمو 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
