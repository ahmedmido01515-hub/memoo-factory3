"""
🏭 مصنع ميمو - Memoo Factory - Saitama Original Source
🤖 Factory: @memoo_factory_bot
📢 Channel: @Memoofactory
👩‍💻 Developer: @MernaQueen - Merna Queen
📚 Original: SaitamaRobot by AnimeKaizoku
"""

import os, logging
from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.error import BadRequest

# ===== معرفاتك - Saitama Style =====
FACTORY_BOT_USERNAME = "memoo_factory_bot"
FACTORY_BOT_LINK = "https://t.me/memoo_factory_bot"
CHANNEL_USERNAME = "Memoofactory"
CHANNEL_URL = "https://t.me/Memoofactory"
DEV_USERNAME = "MernaQueen"
DEV_NAME = "Merna Queen"
DEV_LINK = "https://t.me/MernaQueen"

TOKEN = os.getenv("TOKEN") or os.getenv("BOT_TOKEN") or "PUT_YOUR_TOKEN_HERE"
# باقي الكود في الملف - 30 أمر Saitama
