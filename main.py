# سورس ميمو - Source Memo - النسخة الدائمة V3
# https://t.me/Memoofactory
# @MernaQueen - @memoo_factory_bot

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keep_alive import keep_alive
import config
from database import db
from bot_runner import create_and_run_protection_bot, get_all_bots

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

class MakeBot(StatesGroup):
    waiting_token = State()

def factory_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏭 صنع بوت مجاني", callback_data="make_free")],
        [InlineKeyboardButton(text="💎 صنع بوت مدفوع", callback_data="make_paid")],
        [InlineKeyboardButton(text="📊 احصائيات المصنع", callback_data="stats")],
        [InlineKeyboardButton(text="📢 قناة سورس ميمو", url=config.CHANNEL_LINK)],
    ])

@dp.message(CommandStart())
async def start(message: Message):
    count = len(get_all_bots())
    await message.answer(
        f"أهلا بيك في <b>{config.SOURCE_NAME}</b> 🔥\n\n"
        f"المصنع شغال دائم 24/7\n"
        f"عدد البوتات اللي شغالة حاليا: {count} بوت\n\n"
        f"اختار من تحت:",
        reply_markup=factory_keyboard(), parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("make_"))
async def ask_token(callback: CallbackQuery, state: FSMContext):
    bot_type = callback.data.split("_")[1]
    await state.set_state(MakeBot.waiting_token)
    await state.update_data(bot_type=bot_type)
    await callback.message.answer(f"اخترت بوت {bot_type} 💎\n\nابعت توكن البوت من @BotFather دلوقتي:")
    await callback.answer()

@dp.message(MakeBot.waiting_token)
async def receive_token(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_type = data.get("bot_type", "free")
    token = message.text.strip()

    msg = await message.answer("⏳ بثبت البوت وبشغله بشكل دائم...")
    success, result = await create_and_run_protection_bot(token, bot_type)

    if success:
        await db.add_bot(message.from_user.id, token, bot_type)
        await msg.edit_text(f"✅ بوتك اشتغل وهيـفضل شغال للأبد\nيوزره: {result}\nالنوع: {bot_type}\n\nارفعو ادمن وهيحمي جروبك")
    else:
        await msg.edit_text(f"❌ فشل: {result}")
    await state.clear()

@dp.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):
    all_bots = get_all_bots()
    await callback.message.answer(f"📊 احصائيات سورس ميمو\n\nعدد البوتات الشغالة دائم: {len(all_bots)}\nالمصنع: {config.FACTORY_BOT}\nالمطور: {config.DEVELOPER}")
    await callback.answer()

async def main():
    # ده السحر كله - بيرجع يشغل كل البوتات القديمة لو السيرفر رستر
    keep_alive() # شغل السيرفر الوهمي عشان مينامش
    await db.create_tables()

    old_bots = await db.get_all_bots()
    print(f"[ميمو] لقيت {len(old_bots)} بوت قديم، برجع اشغلهم...")
    for b in old_bots:
        try:
            # b = (user_id, token, type)
            await create_and_run_protection_bot(b[1], b[2])
            await asyncio.sleep(1) # راحة ثانية بين كل بوت والتاني
        except Exception as e:
            print(f"فشل تشغيل بوت قديم: {e}")

    print(f"✅ مصنع {config.SOURCE_NAME} الدائم اشتغل بنجاح")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
