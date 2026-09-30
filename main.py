import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import config
from database import db
from bot_runner import create_and_run_protection_bot

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

class MakeBot(StatesGroup):
    waiting_token = State()

def factory_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏭 صنع بوت مجاني", callback_data="make_free")],
        [InlineKeyboardButton(text="💎 صنع بوت مدفوع", callback_data="make_paid")],
        [InlineKeyboardButton(text="🤖 بوتاتي", callback_data="my_bots")],
        [InlineKeyboardButton(text="📢 قناة السورس", url=config.CHANNEL_LINK)],
    ])

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"أهلا في <b>{config.SOURCE_NAME}</b>\nالمصنع شغال اتوماتيك 24 ساعة ⚡️\n\nاختار نوع البوت:", reply_markup=factory_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("make_"))
async def ask_token(callback: CallbackQuery, state: FSMContext):
    bot_type = callback.data.split("_")[1] # free او paid
    await state.set_state(MakeBot.waiting_token)
    await state.update_data(bot_type=bot_type)
    await callback.message.answer(f"تمام اخترت البوت الـ {bot_type}\n\nدلوقتي روح لـ @BotFather اعمل بوت جديد وهات التوكن والصقه هنا فورا 👇")
    await callback.answer()

@dp.message(MakeBot.waiting_token)
async def receive_token(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_type = data.get("bot_type", "free")
    token = message.text.strip()

    if ":" not in token:
        await message.answer("التوكن ده شكله غلط يا غالي، اتأكد منه تاني")
        return

    msg = await message.answer("⏳ بستلم البوت وبشغلهولك دلوقتي... ثانية واحدة")

    success, result = await create_and_run_protection_bot(token, bot_type)

    if success:
        await db.add_bot(message.from_user.id, token, bot_type)
        await msg.edit_text(f"✅ مبروك! بوتك اشتغل بنجاح\n\nيوزر بوتك: {result}\nنوعه: {bot_type}\n\nروح ارفعه ادمن في جروبك وهو هيحميه لوحده\n\nسورس ميمو - {config.CHANNEL_LINK}")
    else:
        await msg.edit_text(f"❌ فشل التشغيل: {result}\n\nتأكد ان التوكن صح وانك مسحت البوت من مكان تاني لو شغال")

    await state.clear()

async def main():
    await db.create_tables()
    # شغل كل البوتات القديمة اللي كانت محفوظة قبل كده
    old_bots = await db.get_all_bots()
    for b in old_bots:
        await create_and_run_protection_bot(b[1], b[2])

    print(f"مصنع {config.SOURCE_NAME} الاتوماتيك اشتغل 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
