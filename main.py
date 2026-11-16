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
    characters = string.ascii_uppercase + string.digits
    return "YAGAMI-" + "".join(secrets.choice(characters) for _ in range(6))

def authorized(user_id):
    return user_id == ADMIN_ID or user_id in ok

def menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton("CODM TXT", callback_data="codm")],
