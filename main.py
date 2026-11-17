import os
import json
import random
import string
import threading
import base64
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
if "ML" not in stock_files: stock_files["ML"] = []
if "CODM" not in stock_files: stock_files["CODM"] = []
keys = saved.get("keys", {})
authorized_users = set(saved.get("authorized_users", []))
waiting_upload = {}

def locked_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔑 REDEEM KEY", callback_data="redeem")]])

def main_menu(user_id):
    buttons = [
        [InlineKeyboardButton("📄 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("📄 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("🔑 REDEEM KEY", callback_data="redeem"), InlineKeyboardButton("📊 MY STATISTICS", callback_data="stats")],
    ]
    if user_id == OWNER_ID:
        buttons.append([InlineKeyboardButton("🛠 GENERATE KEY", callback_data="generate")])
        buttons.append([InlineKeyboardButton("📤 UPLOAD ML TXT", callback_data="upload_ml")])
        buttons.append([InlineKeyboardButton("📤 UPLOAD CODM TXT", callback_data="upload_codm")
