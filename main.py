import os
import json
import random
import string
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8089763801
OWNER_USERNAME = "@yagami_owner"
STOCK_FILE = "stock.json"

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
        buttons.append([InlineKeyboardButton("📤 UPLOAD CODM TXT", callback_data="upload_codm")])
        buttons.append([InlineKeyboardButton("🗑 CLEAR ML STOCK", callback_data="clear_ml")])
        buttons.append([InlineKeyboardButton("🗑 CLEAR CODM STOCK", callback_data="clear_codm")])
        buttons.append([InlineKeyboardButton("🛠 ULP & DUPLICATE REMOVER", callback_data="ulp")])
        buttons.append([InlineKeyboardButton("🛡 DATADOME GENERATOR", callback_data="datadome")])
    return InlineKeyboardMarkup(buttons)

def is_authorized(user_id):
    return user_id == OWNER_ID or user_id in authorized_users

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_authorized(user_id):
        await update.message.reply_text("👋 Welcome to YAGAMI Bot! Choose below:", reply_markup=main_menu(user_id))
    else:
        await update.message.reply_text("🔒 LOCKED!\n\nThis bot is locked. You need an Entrance Key to access the panel.\n\nClick REDEEM KEY and send your key.", reply_markup=locked_menu())

# --- BAGO DITO BOSS: WARNING PAG BUYER NAG /newkey ---
async def newkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        # PULA NA WARNING PARA SA BUYER
        await update.message.reply_text(f"⛔ WARNING!\n\n❌ Only {OWNER_USERNAME} can generate key!\n\nYou are not allowed to use this command. Contact {OWNER_USERNAME} to buy a key.")
        return
    # KUNG IKAW, GAGAWA SYA NG KEY
    new_key = "YAGAMI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    keys[new_key] = True
    save_data()
    await update.message.reply_text(f"✅ Your New Entrance Key:\n`{new_key}`\n\nGive this to your buyer.", parse_mode="Markdown")

async def ml_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🔒 LOCKED! You need an Entrance Key first. Click REDEEM KEY.", reply_markup=locked_menu())
        return
    files = stock_files.get("ML", [])
    if not files:
        await update.message.reply_text("❌ No stock yet for ML TXT. Please wait for Boss to upload.")
        return
    await update.message.reply_text(f"📄 Sending {len(files)} file(s) of ML...")
    for file_id in files:
        try:
            await context.bot.send_document(chat_id=update.message.chat_id, document=file_id, caption="📄 ML TXT")
        except:
            pass

async def codm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🔒 LOCKED! You need an Entrance Key first. Click REDEEM KEY.", reply_markup=locked_menu())
        return
    files = stock_files.get("CODM", [])
    if not files:
        await update.message.reply_text("❌ No stock yet for CODM TXT. Please wait for Boss to upload.")
        return
    await update.message.reply_text(f"📄 Sending {len(files)} file(s) of CODM...")
    for file_id in files:
        try:
            await context.bot.send_document(chat_id=update.message.chat_id, document=file_id, caption="📄 CODM TXT")
        except:
            pass

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"❓ HELP\n\n/start - Open panel\n/ml - Get ML TXT\n/codm - Get CODM TXT\n/newkey - Admin Only, only {OWNER_USERNAME} can generate key\n\nTo buy a key, contact {OWNER_USERNAME}")
# --- END BAGO ---

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try: await query.answer()
    except: pass
    user_id = query.from_user.id
    data = query.data
    if data == "redeem":
        await query.edit_message_text("🔑 Send your ENTRANCE KEY here.")
        context.user_data["waiting_key"] = True
        return
    if not is_authorized(user_id):
        await query.edit_message_text("🔒 LOCKED!\n\nYou need an Entrance Key first. Click REDEEM KEY.", reply_markup=locked_menu())
        return
    if data in ["ml_txt", "codm_txt"]:
        key = "ML" if data == "ml_txt" else "CODM"
        files = stock_files.get(key, [])
        if not files:
            await query.edit_message_text(f"❌ No stock yet for {key} TXT. Please wait for Boss to upload.")
            return
        await query.edit_message_text(f"📄 Sending {len(files)} file(s) of {key}...")
        for file_id in files:
            try: await context.bot.send_document(chat_id=query.message.chat_id, document=file_id, caption=f"📄 {key} TXT")
            except: await context.bot.send_message(chat_id=query.message.chat_id, text="⚠️ Failed to send one file, tell Boss to re-upload.")
        return
    if data in ["upload_ml", "upload_codm"]:
        if user_id != OWNER_ID:
            await query.answer("Admin only!", show_alert=True)
            return
        key = "ML" if data == "upload_ml" else "CODM"
        waiting_upload[user_id] = key
        await query.edit_message_text(f"📤 Send your {key} .txt FILES here. Current stock: {len(stock_files.get(key, []))} file(s).")
        return
    if data in ["clear_ml", "clear_codm"]:
        if user_id != OWNER_ID: return
        key = "ML" if data == "clear_ml" else "CODM"
        stock_files[key] = []
        save_data()
        await query.edit_message_text(f"🗑 {key} stock cleared.")
        return
    if data == "generate":
        if user_id != OWNER_ID: return
        new_key = "YAGAMI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        keys[new_key] = True
        save_data()
        await query.edit_message_text(f"✅ Your New Entrance Key:\n`{new_key}`\n\nGive this to your buyer.", parse_mode="Markdown")
        return
    if data == "stats":
        await query.edit_message_text(f"📊 MY STATISTICS\n\n📄 ML Stock: {len(stock_files.get('ML', []))} file(s)\n📄 CODM Stock: {len(stock_files.get('CODM', []))} file(s)\n👥 Authorized Users: {len(authorized_users)}\n🔑 Unused Keys: {len(keys)}")
        return
    if data == "ulp":
        await query.edit_message_text("🧹 ULP & DUPLICATE REMOVER\nSend your .txt file here.")
        return
    if data == "datadome":
        await query.edit_message_text("🛡 DATADOME GENERATOR\nComing soon Boss!")
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in waiting_upload and update.message.document:
        key = waiting_upload[user_id]
        stock_files[key].append(update.message.document.file_id)
        save_data()
        await update.message.reply_text(f"✅ SAVED! Now you have {len(stock_files[key])} file(s) in {key}.")
        return
    if context.user_data.get("waiting_key") and update.message.text:
        key = update.message.text.strip()
        if key in keys:
            del keys[key]
            authorized_users.add(user_id)
            save_data()
            context.user_data["waiting_key"] = False
            await update.message.reply_text("✅ KEY ACCEPTED! Panel unlocked!", reply_markup=main_menu(user_id))
        else:
            await update.message.reply_text("❌ Invalid Key. Try again or contact Boss.")
        return

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newkey", newkey_command))
    app.add_handler(CommandHandler("ml", ml_command))
    app.add_handler(CommandHandler("codm", codm_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, handle_message))
    print(f"Bot is running... ML: {len(stock_files.get('ML', []))} files, CODM: {len(stock_files.get('CODM', []))} files")
    app.run_polling()

if __name__ == "__main__":
    main()
