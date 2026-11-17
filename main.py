import os
import json
import random
import string
import asyncio
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 123456789
OWNER_USERNAME = "@YouknowLight"
DATA_FILE = "data.json"

try:
    OWNER_ID = int(os.environ.get("ADMIN_ID", str(OWNER_ID)))
except:
    pass

def is_owner(user_id):
    try:
        return int(user_id) == int(OWNER_ID)
    except:
        return False

GAMES = ["ML", "CODM", "COC", "GMAIL", "GLOBAL"]
GAME_NAME = {"ML": "ML", "CODM": "CODM", "COC": "COC", "GMAIL": "GMAIL", "GLOBAL": "GLOBAL-CODM"}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"keys": {}, "users": {}, "stock_files": {g: [] for g in GAMES}}
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            if "stock_files" not in d:
                d["stock_files"] = {}
            for g in GAMES:
                if g not in d["stock_files"]:
                    d["stock_files"][g] = []
                new_list = []
                for x in d["stock_files"].get(g, []):
                    if isinstance(x, str):
                        new_list.append({"name": x, "file_id": None})
                    else:
                        new_list.append(x)
                d["stock_files"][g] = new_list
            return d
    except:
        return {"keys": {}, "users": {}, "stock_files": {g: [] for g in GAMES}}

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

def main_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("🎮 GENERATE 10 DAYS", callback_data="gen_10")],
        [InlineKeyboardButton("🎮 GENERATE 20 DAYS", callback_data="gen_20")],
        [InlineKeyboardButton("🎮 GENERATE 50 DAYS", callback_data="gen_50")],
        [InlineKeyboardButton("👑 GENERATE LIFETIME", callback_data="gen_lifetime")],
        [InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")],
        [InlineKeyboardButton("📄 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("📄 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("📄 COC TXT", callback_data="coc_txt"), InlineKeyboardButton("📄 GMAIL TXT", callback_data="gmail_txt")],
        [InlineKeyboardButton("📄 GLOBAL-CODM TXT", callback_data="global_txt")],
        [InlineKeyboardButton("📤 UPLOAD ML", callback_data="upload_ml"), InlineKeyboardButton("📤 UPLOAD CODM", callback_data="upload_codm")],
        [InlineKeyboardButton("📤 UPLOAD COC", callback_data="upload_coc"), InlineKeyboardButton("📤 UPLOAD GMAIL", callback_data="upload_gmail")],
        [InlineKeyboardButton("📤 UPLOAD GLOBAL-CODM", callback_data="upload_global")],
        [InlineKeyboardButton("📊 STATS", callback_data="stats"), InlineKeyboardButton("👤 MY STATUS", callback_data="status")],
    ]
    return InlineKeyboardMarkup(keyboard)

def user_menu():
    keyboard = [
        [InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")],
        [InlineKeyboardButton("📄 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("📄 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("📄 COC TXT", callback_data="coc_txt"), InlineKeyboardButton("📄 GMAIL TXT", callback_data="gmail_txt")],
        [InlineKeyboardButton("📄 GLOBAL-CODM TXT", callback_data="global_txt")],
        [InlineKeyboardButton("👤 MY STATUS", callback_data="status")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_menu(user_id=None):
    if user_id is not None and is_owner(user_id):
        return main_menu(user_id)
    return user_menu()

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ BACK", callback_data="back")]])

def redeem_only_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _uid = None
    if update.message:
        _uid = update.message.from_user.id
    elif update.callback_query:
        _uid = update.callback_query.from_user.id
    if _uid is not None and is_owner(_uid):
        text = "👋 **WELCOME TO YAGAMI BOT**\n\nOwner: @YouknowLight 👑\n\nChoose:\n• Generate Key\n• Redeem Key\n• ML / CODM
