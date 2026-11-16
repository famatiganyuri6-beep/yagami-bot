import os
import secrets
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

keys = set()
ok = set()

def mk():
    return "YAGAMI-" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

def authorized(user_id):
    return user_id == ADMIN_ID or user_id in ok

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
