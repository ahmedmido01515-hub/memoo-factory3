# سورس ميمو - Source Memo - نظام التشغيل الاتوماتيك
# قناة السورس: https://t.me/Memoofactory
# المطور: @MernaQueen
# المصنع: @memoo_factory_bot

import asyncio
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

# ده القالب الجاهز لبوت الحماية اللي هيتصنع
# كل بوت جديد بيتعمله مجلد لوحده

RUNNING_BOTS = {} # عشان نعرف البوتات اللي شغالة دلوقتي

async def create_and_run_protection_bot(bot_token: str, bot_type: str = "free"):
    """
    الوظيفة دي بتاخد توكن العميل وبتشغل بوت حماية جديد فورا
    bot_type: free او paid
    """
    if bot_token in RUNNING_BOTS:
        return False, "البوت ده شغال عندي اصلا يا باشا"

    try:
        # بنجرب التوكن شغال ولا لا
        temp_bot = Bot(token=bot_token)
        me = await temp_bot.get_me()
        await temp_bot.session.close()

        # بنستورد منطق الحماية
        from protection_logic import get_protection_dispatcher

        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode="HTML"))
        dp = get_protection_dispatcher(bot_type) # بيجيب الحماية حسب النوع مجاني ولا مدفوع

        # بنشغل البوت في الخلفية
        task = asyncio.create_task(dp.start_polling(bot))
        RUNNING_BOTS[bot_token] = {
            "task": task,
            "username": me.username,
            "type": bot_type,
            "bot": bot
        }

        print(f"[ميمو] تم تشغيل بوت جديد: @{me.username} - النوع: {bot_type}")
        return True, f"@{me.username}"

    except Exception as e:
        print(f"[خطأ ميمو] فشل تشغيل البوت: {e}")
        return False, str(e)

async def stop_bot(bot_token: str):
    if bot_token in RUNNING_BOTS:
        RUNNING_BOTS[bot_token]["task"].cancel()
        await RUNNING_BOTS[bot_token]["bot"].session.close()
        del RUNNING_BOTS[bot_token]
        return True
    return False

def get_all_bots():
    return RUNNING_BOTS
