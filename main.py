import os
import json
import random
import string
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ============ CONFIG ============
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 123456789
DATA_FILE = "data.json"

# ============ ADDED ONLY - OWNER LOCK ============
# Get real OWNER ID from Render ADMIN_ID = 8089763801
# If no ADMIN_ID, it will use OWNER_ID above
try:
    OWNER_ID = int(os.environ.get("ADMIN_ID", str(OWNER_ID)))
except:
    pass

def is_owner(user_id):
    try:
        return int(user_id) == int(OWNER_ID)
    except:
        return False
# ============ END ADDED ============

# ============ DATA ============
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"keys": {}, "users": {}, "stock_files": {"ML": [], "CODM": []}}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"keys": {}, "users": {}, "stock_files": {"ML": [], "CODM": []}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

DATA = load_data()
keys_db = DATA["keys"]
users_db = DATA["users"]
stock_files = DATA["stock_files"]
waiting_redeem = set()
waiting_upload = {}

def gen_key():
    return "YAGAMI-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

def is_authorized(user_id):
    if user_id == OWNER_ID:
        return True
    u = users_db.get(str(user_id))
    if not u:
        return False
    exp = u.get("expire", "")
    if exp == "LIFETIME":
        return True
    try:
        return datetime.fromisoformat(exp) > datetime.now()
    except:
        return False

# ============ MENUS ============
def main_menu(user_id=None):
    # OWNER MENU - Full access
    keyboard = [
        [InlineKeyboardButton("🎮 GENERATE 10 DAYS", callback_data="gen_10")],
        [InlineKeyboardButton("🎮 GENERATE 20 DAYS", callback_data="gen_20")],
        [InlineKeyboardButton("🎮 GENERATE 50 DAYS", callback_data="gen_50")],
        [InlineKeyboardButton("👑 GENERATE LIFETIME", callback_data="gen_lifetime")],
        [InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")],
        [InlineKeyboardButton("📄 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("📄 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("📤 UPLOAD ML", callback_data="upload_ml"), InlineKeyboardButton("📤 UPLOAD CODM", callback_data="upload_codm")],
        [InlineKeyboardButton("📊 STATS", callback_data="stats"), InlineKeyboardButton("👤 MY STATUS", callback_data="status")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ============ ADDED ONLY - USER MENU ============
def user_menu():
    # BUYER / USER MENU - No Generate, No Upload, No Stats
    keyboard = [
        [InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")],
        [InlineKeyboardButton("📄 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("📄 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("👤 MY STATUS", callback_data="status")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_menu(user_id=None):
    if user_id is not None and is_owner(user_id):
        return main_menu(user_id)
    return user_menu()
# ============ END ADDED ============

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ BACK", callback_data="back")]])

# ============ START ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ADDED ONLY - Detect if owner or user
    _uid = None
    if update.message:
        _uid = update.message.from_user.id
    elif update.callback_query:
        _uid = update.callback_query.from_user.id
    _menu = get_menu(_uid)
    # END ADDED

    text = (
        "👋 **WELCOME TO YAGAMI BOT**\n\n"
        "Choose:\n"
        "• Generate Key\n"
        "• Redeem Key\n"
        "• ML / CODM TXT\n"
        "• Upload Files\n\n"
        "Bot is Online ✅"
    )
    # ADDED ONLY - Different text for buyer/user
    if _uid is not None and not is_owner(_uid):
        text = (
            "👋 **WELCOME TO YAGAMI BOT**\n\n"
            "Choose:\n"
            "• Redeem Key\n"
            "• ML / CODM TXT\n"
            "• My Status\n\n"
            "Bot is Online ✅"
        )
    # END ADDED

    if update.message:
        await update.message.reply_text(text, reply_markup=_menu, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=_menu, parse_mode="Markdown")

# ============ BUTTONS ============
async def button_handler(update: Update, context: Context
