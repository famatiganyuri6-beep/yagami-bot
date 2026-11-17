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
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"keys": {}, "users": {}, "stock_files": {"ML": [], "CODM": [], "COC": [], "GMAIL": [], "GLOBAL-CODM": []}}
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            for k in ["ML", "CODM", "COC", "GMAIL", "GLOBAL-CODM"]:
                if k not in d.get("stock_files", {}):
                    d["stock_files"][k] = []
            return d
    except:
        return {"keys": {}, "users": {}, "stock_files": {"ML": [], "CODM": [], "COC": [], "GMAIL": [], "GLOBAL-CODM": []}}
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
