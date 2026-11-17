import os
import json
import random
import string
import threading
import base64
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8089763801
OWNER_USERNAME = "@yagami_owner"
STOCK_FILE = "stock.json"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"YAGAMI Bot is running!")
    def log_message(self, format, *args):
        pass
def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
threading.Thread(target=run_web_server, daemon=True).start()
def load_data():
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{STOCK_FILE}?ref={GITHUB_BRANCH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                content = base64.b64decode(r.json()["content"]).decode()
                return json.loads(content)
        except Exception as e:
            print(f"GitHub load failed: {e}")
    if os.path.exists(STOCK_FILE):
        try:
            with open(STOCK_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"stock_files": {"ML": [], "CODM": []}, "keys": {}, "authorized_users": []}
def save_data():
    data = {"stock_files": stock_files, "keys": keys, "authorized_users": list(authorized_users)}
    with open(STOCK_FILE, "w") as f:
        json.dump(data, f)
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{STOCK_FILE}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            r = requests.get(url, headers=headers, params={"ref": GITHUB_BRANCH}, timeout=10)
            sha = r.json().get("sha") if r.status_code == 200 else None
            content = base64.b64encode(json.dumps(data).encode()).decode()
            payload = {"message": "Update stock", "content": content, "branch": GITHUB_BRANCH}
            if sha:
                payload["sha"] = sha
            requests.put(url, headers=headers, json=payload, timeout=10)
            print("Saved to GitHub - PERMANENT")
        except Exception as e:
            print(f"GitHub save failed: {e}")
saved = load_data()
stock_files = saved.get("stock_files", {"ML": [], "CODM": []})
if "ML" not in stock_files:
    stock_files["ML"] = []
if "CODM" not in stock_files:
    stock_files["CODM"] = []
keys = saved.get("keys", {})
authorized_users = set(saved.get("authorized_users", []))
waiting_upload = {}
def locked_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("REDEEM KEY", callback_data="redeem")]])
def main_menu(user_id):
    buttons = []
    buttons.append([InlineKeyboardButton("ML TXT", callback_data="ml_txt"), InlineKeyboardButton("CODM TXT", callback_data="codm_txt")])
    buttons.append([InlineKeyboardButton("REDEEM KEY", callback_data="redeem"), InlineKeyboardButton("MY STATISTICS", callback_data="stats")])
    if user_id == OWNER_ID:
        buttons.append([InlineKeyboardButton("GENERATE 10 DAYS", callback_data="generate_10days")])
        buttons.append([InlineKeyboardButton("GENERATE 20 DAYS", callback_data="generate_20days")])
        buttons.append([InlineKeyboardButton("GENERATE 50 DAYS", callback_data="generate_50days")])
        buttons.append([InlineKeyboardButton("GENERATE LIFETIME", callback_data="generate_lifetime")])
        buttons.append([InlineKeyboardButton("UPLOAD ML TXT", callback_data="upload_ml")])
        buttons.append([InlineKeyboardButton("UPLOAD CODM TXT", callback_data="upload_codm")])
        buttons.append([InlineKeyboardButton("CLEAR ML STOCK", callback_data="clear_ml")])
        buttons.append([InlineKeyboardButton("CLEAR CODM STOCK", callback_data="clear_codm")])
        buttons.append([InlineKeyboardButton("ULP & DUPLICATE REMOVER", callback_data="ulp")])
        buttons.append([InlineKeyboardButton("DATADOME GENERATOR", callback_data="datadome")])
    return InlineKeyboardMarkup(buttons)
def is_authorized(user_id):
    return user_id == OWNER_ID or user_id in authorized_users
def check_key_expiry(key):
    info = keys.get(key)
    if not info:
        return False
    if isinstance(info, bool):
        return True
    if isinstance(info, str):
        return True
    expiry = info.get("expiry")
    if expiry is None:
        return True
    if time.time() > expiry:
        del keys[key]
        save_data()
        return False
    return True
def get_key_type(key):
    info = keys.get(key)
    if isinstance(info, dict):
        return info.get("type", "UNKNOWN")
    return "OLD KEY"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_authorized(user_id):
        await update.message.reply_text("Welcome to YAGAMI Bot! Choose below:", reply_markup=main_menu(user_id))
    else:
        await update.message.reply_text("LOCKED!\n\nThis bot is locked. You need an Entrance Key to access the panel.\n\nClick REDEEM KEY and send your key.", reply_markup=locked_menu())
async def newkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text(f"WARNING!\n\nOnly {OWNER_USERNAME} can generate key!")
        return
    await update.message.reply_text("Pili ka boss:\n\n/generate10 - 10 Days Key\n/generate20 - 20 Days Key\n/generate50 - 50 Days Key\n/generatelife - Lifetime Key")
async def generate_days_command(update: Update, context: ContextTypes.DEFAULT_TYPE, days):
    if update.effective_user.id != OWNER_ID:
        return
    new_key = f"YAGAMI-{days}D-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    expiry = time.time() + (days * 24 * 60 * 60)
    keys[new_key] = {"expiry": expiry, "type": f"{days}DAYS"}
    save_data()
    await update.message.reply_text(f"Your New {days} DAYS Key:\n`{new_key}`\n\nMag-e-expire to after {days} days.", parse_mode="Markdown")
async def generate10_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_days_command(update, context, 10)
async def generate20_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_days_command(update, context, 20)
async def generate50_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_days_command(update, context, 50)
async def generatelife_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    new_key = "YAGAMI-LIFE-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    keys[new_key] = {"expiry": None, "type": "LIFETIME"}
    save_data()
    await update.message.reply_text(f"Your New LIFETIME Key:\n`{new_key}`\n\nHindi to mag-e-expire.", parse_mode="Markdown")
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    if data.startswith("generate_"):
        if user_id != OWNER_ID:
            return
        if data == "generate_lifetime":
            new_key = "YAGAMI-LIFE-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            keys[new_key] = {"expiry": None, "type": "LIFETIME"}
            save_data()
            await query.edit_message_text(f"Your New LIFETIME Key:\n`{new_key}`\n\nHindi to mag-e-expire.", parse_mode="Markdown")
        else:
            days_map = {"generate_10days": 10, "generate_20days": 20, "generate_50days": 50}
            days = days_map.get(data, 10)
            new_key = f"YAGAMI-{days}D-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            expiry = time.time() + (days * 24 * 60 * 60)
            keys[new_key] = {"expiry": expiry, "type": f"{days}DAYS"}
            save_data()
            await query.edit_message_text(f"Your New {days} DAYS Key:\n`{new_key}`\n\nMag-e-expire to after {days} days.", parse_mode="Markdown")
        return
    if data == "redeem":
        context.user_data["waiting"] = "key"
        await query.edit_message_text("Send mo yung KEY mo:")
        return
    if data == "stats":
        if not is_authorized(user_id):
            await query.edit_message_text("LOCKED! Redeem key first.", reply_markup=locked_menu())
            return
        await query.edit_message_text(f"MY STATISTICS\n\nML Stock: {len(stock_files['ML'])} files\nCODM Stock: {len(stock_files['CODM'])} files\nTotal Users: {len(authorized_users)}", reply_markup=main_menu(user_id))
        return
    if data in ["ml_txt", "codm_txt"]:
        if not is_authorized(user_id):
            await query.edit_message_text("LOCKED! Redeem key first.", reply_markup=locked_menu())
            return
        game = "ML" if data == "ml_txt" else "CODM"
        files = stock_files.get(game, [])
        if not files:
            await query.edit_message_text(f"Walang {game} stock pa.", reply_markup=main_menu(user_id))
            return
        await query.edit_message_text(f"Sending {game} TXT...", reply_markup=main_menu(user_id))
        for f in files:
            try:
                await query.message.reply_document(document=f["file_id"], caption=f.get("name", f"{game} TXT"))
            except:
                pass
        return
    if data in ["upload_ml", "upload_codm"]:
        if user_id != OWNER_ID:
            return
        game = "ML" if data == "upload_ml" else "CODM"
        waiting_upload[user_id] = game
        await query.edit
