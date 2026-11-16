import os
import glob
import asyncio
from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext import ContextTypes
from telegram.ext import filters

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# PALITAN MO TO NG GUSTO MONG ENTRANCE KEY
ENTRANCE_KEY = "YAGAMI-ENTER"

players = {}
used_keys = set()
authorized = set()

def get_txt_files():
    files = glob.glob("*.txt")
    files = [f for f in files if f != "requirements.txt"]
    return sorted(files)

def main_menu():
    k = []
    k.append([InlineKeyboardButton("Games", callback_data="games")])
    k.append([InlineKeyboardButton("Register", callback_data="register")])
    k.append([InlineKeyboardButton("Tournament", callback_data="tournament")])
    k.append([InlineKeyboardButton("Files", callback_data="files")])
    k.append([InlineKeyboardButton("Help", callback_data="help")])
    return InlineKeyboardMarkup(k)

def back_btn():
    k = []
    k.append([InlineKeyboardButton("Back", callback_data="back")])
    return InlineKeyboardMarkup(k)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in authorized:
        txt = "Welcome back to yagami_bot!\nChoose an option below:"
        await update.message.reply_text(txt, reply_markup=main_menu())
        return
    txt = "Welcome to yagami_bot!\n\nThis bot is LOCKED.\nEnter Entrance Key to continue:"
    await update.message.reply_text(txt)

async def check_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in authorized:
        return
    text = update.message.text.strip()
    if text == ENTRANCE_KEY:
        authorized.add(uid)
        await update.message.reply_text("Key Accepted! Welcome!", reply_markup=main_menu())
    else:
        await update.message.reply_text("Wrong Key! Try again.\nEnter Entrance Key:")

async def register_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in authorized:
        await update.message.reply_text("Locked! Send Entrance Key first. Type /start")
        return
    if not context.args:
        await update.message.reply_text("Type: /register <Your IGN>")
        return
    ign = " ".join(context.args)
    uid = update.effective_user.id
    players[uid] = ign
    await update.message.reply_text("Registered: " + ign)

async def redeem_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in authorized:
        await update.message.reply_text("Locked! Send Entrance Key first. Type /start")
        return
    if not context.args:
        await update.message.reply_text("Type: /redeem <KEY>")
        return
    key = context.args[0]
    if key in used_keys:
        await update.message.reply_text("Key already used!")
        return
    used_keys.add(key)
    ign = players.get(update.effective_user.id, "Unknown")
    txt = "Key Redeemed!\nKey: " + key + "\nPlayer: " + ign
    await update.message.reply_text(txt)

async def tournament_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in authorized:
        await update.message.reply_text("Locked! Send Entrance Key first. Type /start")
        return
    txt = "CODM 20261116 Tournament\nPlayers: " + str(len(players))
    txt += "\nType /register <IGN> to join!"
    await update.message.reply_text(txt)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id not in authorized:
        await query.edit_message_text("Locked! Send Entrance Key first. Type /start")
        return
    data = query.data
    if data == "back":
        txt = "Welcome to yagami_bot!\nChoose an option below:"
        await query.edit_message_text(txt, reply_markup=main_menu())
        return
    if data == "games":
        txt = "Games:\nCODM Tournament\nMix Codm\nClean Codm"
        await query.edit_message_text(txt, reply_markup=back_btn())
        return
    if data == "register":
        txt = "Register CODM\nType: /register <Your IGN>"
        await query.edit_message_text(txt, reply_markup=back_btn())
        return
    if data == "tournament":
        txt = "CODM 20261116 Tournament\nPlayers: " + str(len(players))
        await query.edit_message_text(txt, reply_markup=back_btn())
        return
    if data == "files":
        files = get_txt_files()
        k = []
        for f in files:
            short = f
            if len(f) > 
