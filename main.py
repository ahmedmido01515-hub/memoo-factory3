import asyncio
import logging
import config
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from bot_runner import create_and_run_protection_bot, get_all_bots
from keep_alive import keep_alive

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

class MakeBot(StatesGroup):
    waiting_token = State()

def factory_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="صنع بوت مجاني", callback_data="make_free")],
        [InlineKeyboardButton(text="صنع بوت مدفوع", callback_data="make_paid")],
        [InlineKeyboardButton(text="احصائيات", callback_data="stats")],
    ])

@dp.message(CommandStart())
async def start_handler(message: Message):
    count = len(get_all_bots())
    text = f"اهلا في {config.SOURCE_NAME}\nالبوتات الشغالة: {count}\nاختر من تحت"
    await message.answer(text, reply_markup=factory_keyboard())

@dp.callback_query(F.data == "make_free")
async def ask_free(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MakeBot.waiting_token)
    await state.update_data(bot_type="free")
    await callback.message.answer("ابعت توكن البوت من @BotFather")
    await callback.answer()

@dp.callback_query(F.data == "make_paid")
async def ask_paid(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="كلم المطور @mernaqueen", url="https://t.me/mernaqueen")],
        [InlineKeyboardButton(text="رجوع", callback_data="back_home")]
    ])
    await callback.message.edit_text(f"البوت المدفوع سعره {config.PAID_BOT_PRICE} جنيه\nكلم المطور @mernaqueen للدفع", reply_markup=kb)
    await callback.answer()

@dp.callback_query(F.data == "back_home")
async def back_home(callback: CallbackQuery):
    await callback.message.edit_text(f"اهلا في {config.SOURCE_NAME}", reply_markup=factory_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):
    await callback.message.answer(f"عدد البوتات الشغالة: {len(get_all_bots())}")
    await callback.answer()

@dp.message(MakeBot.waiting_token)
async def get_token(message: Message, state: FSMContext):
    data = await state.get_data()
    b_type = data.get("bot_type", "free")
    token = message.text.strip()
    if ":" not in token:
        await message.answer("التوكن غلط")
        return
    m = await message.answer("بشغل البوت...")
    ok, res = await create_and_run_protection_bot(token, b_type)
    if ok:
        await db.add_bot(message.from_user.id, token, b_type)
        await m.edit_text(f"تم تشغيل بوتك: {res}")
    else:
        await m.edit_text(f"فشل: {res}")
    await state.clear()

@dp.message(F.text.startswith("/فعل"))
async def admin_active(message: Message):
    if message.from_user.id!= config.ADMIN_ID:
        return
    try:
        parts = message.text.split()
        token = parts[1]
        uid = int(parts[2])
        ok, res = await create_and_run_protection_bot(token, "paid")
        if ok:
            await db.add_bot(uid, token, "paid")
            await message.reply(f"تم تفعيل المدفوع: {res} للعميل {uid}")
            try:
                await bot.send_message(uid, f"تم تفعيل بوتك المدفوع: {res}")
            except:
                pass
        else:
            await message.reply(f"فشل: {res}")
    except Exception as e:
        await message.reply(f"الاستخدام: /فعل توكن ايدي\n{e}")

async def main():
    keep_alive()
    await db.create_tables()
    old = await db.get_all_bots()
    for b in old:
        try:
            await create_and_run_protection_bot(b[1], b[2])
            await asyncio.sleep(1)
        except:
            pass
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
