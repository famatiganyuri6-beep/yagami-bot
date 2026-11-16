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

def menu(is_admin=False):
    buttons = []
    buttons.append([InlineKeyboardButton("CODM TXT", callback_data="codm")])
    buttons.append([InlineKeyboardButton("ML TXT", callback_data="ml")])
    if is_admin == True:
        buttons.append([InlineKeyboardButton("Generate Key", callback_data="genkey")])  # <- AYAN AYOS NA
    buttons.append([InlineKeyboardButton("Help", callback_data="help")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        ok.add(user_id)
        await update.message.reply_text("Welcome Admin!", reply_markup=menu(True))
    elif user_id not in ok:
        await update.message.reply_text("LOCKED. Enter Key:")
    else:
        await update.message.reply_text("Welcome!", reply_markup=menu(False))

async def newkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    key = mk()
    keys.add(key)
    await update.message.reply_text("New Key: " + key)

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "codm":
        await query.message.reply_text("Send CODM .txt")
    if query.data == "ml":
        await query.message.reply_text("Send ML .txt")
    if query.data == "genkey" and query.from_user.id == ADMIN_ID:
        key = mk()
        keys.add(key)
        await query.message.reply_text("New Key:
