import os
import secrets
import string
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from flask import Flask

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
        [InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")],
        [InlineKeyboardButton("🔥 ML TXT", callback_data="ml")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton("🔑 Generate Key", callback_data="genkey")])
    buttons.append([InlineKeyboardButton("❓ Help", callback_data="help")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        ok.add(user_id)
        await update.message.reply_text("👑 Welcome to YAGAMI BOT, Admin!", reply_markup=menu(True))
    elif user_id not in ok:
        await update.message.reply_text("🔒 Welcome to YAGAMI BOT\n\nThis bot is LOCKED.\nPlease enter your Entrance Key:")
    else:
        await update.message.reply_text("👋 Welcome to YAGAMI BOT!", reply_markup=menu(False))

async def newkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Only Admin can generate keys.")
        return
    key = mk()
    keys.add(key)
    await update.message.reply_text(f"🔑 New Key:\n\n`{key}`", parse_mode="Markdown")

async def codm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update.effective_user.id):
        await update.message.reply_text("🔒 Access denied.")
        return
    await update.message.reply_text("🎮 CODM TXT\n\nSend your CODM .txt file here.")

async def ml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update.effective_user.id):
        await update.message.reply_text("🔒 Access denied.")
        return
    await update.message.reply_text("🔥 ML TXT\n\nSend your ML .txt file here.")

async def hlp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ HELP\n\n1. Type /start\n2. Enter your Entrance Key\n3. Press CODM TXT or ML TXT\n4. Send your .txt file")

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if not authorized(user_id):
        await query.message.reply_text("🔒 Access denied.")
        return
    
    if query.data == "codm":
        await query.message.reply_text("🎮 CODM TXT\n\nSend your CODM .txt file here.")
    elif query.data == "ml":
        await query.message.reply_text("🔥 ML TXT
