import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

RUNNING_BOTS = {}

def get_all_bots():
    return RUNNING_BOTS

def get_protection_dispatcher(bot_type="free"):
    dp = Dispatcher()
    @dp.message(Command("start"))
    async def s(m: Message): 
        await m.answer(f"بوت حماية شغال من سورس ميمو - النوع {bot_type}")
    @dp.message(F.text.regexp(r"https?://|t\.me/"))
    async def l(m: Message):
        try: await m.delete()
        except: pass
    return dp

async def create_and_run_protection_bot(bot_token: str, bot_type: str="free"):
    if bot_token in RUNNING_BOTS: 
        return False, "البوت شغال بالفعل"
    try:
        tmp = Bot(token=bot_token)
        me = await tmp.get_me()
        await tmp.session.close()
        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode="HTML"))
        dp = get_protection_dispatcher(bot_type)
        task = asyncio.create_task(dp.start_polling(bot))
        RUNNING_BOTS[bot_token] = {"task": task, "username": me.username, "bot": bot}
        return True, f"@{me.username}"
    except Exception as e: 
        return False, str(e)
