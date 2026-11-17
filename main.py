import random
import string
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "9073043795:AAED3C1-agE_PHcqHUxtzl3ThHZQCvEZZTY"
OWNER_ID = 8089763801
keys = {}
authorized = set()
authorized.add(OWNER_ID)

def make_key():
    chars = string.ascii_letters + string.digits
    return "YAGAMI-" + "".join(random.choice(chars) for _ in range(12))

def get_panel(user_id):
    buttons = [
        [InlineKeyboardButton("📄 CODM TXT", callback_data="codm"), InlineKeyboardButton("📄 ML TXT", callback_data="ml")],
        [InlineKeyboardButton("🔑 REDEEM KEY", callback_data="redeem"), InlineKeyboardButton("📊 MY STATISTICS", callback_data="stats")],
    ]
    if user_id == OWNER_ID:
        buttons.append([InlineKeyboardButton("🛠 GENERATE KEY", callback_data="gen")])
    buttons.append([InlineKeyboardButton("🛠 ULP & DUPLICATE REMOVER", callback_data="ulp")])
    buttons.append([InlineKeyboardButton("🛡 DATADOME GENERATOR", callback_data="datadome")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in authorized:
        await update.message.reply_text("Welcome back, Boss! Choose below:", reply_markup=get_panel(user_id))
    else:
        await update.message.reply_text("Welcome to YAGAMI Bot!\n\nEnter YAGAMI Bot Key:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text.startswith("YAGAMI-"):
        if text in keys:
            del keys[text]
            authorized.add(user_id)
            await update.message.reply_text("Key Accepted! Welcome to YAGAMI Panel.", reply_markup=get_panel(user_id))
        else:
            await update.message.reply_text("Invalid or Used Key! Buy one from admin.")
    else:
        if user_id in authorized:
            await update.message.reply_text("Choose below:", reply_markup=get_panel(user_id))
        else:
            await update.message.reply_text("Please Enter YAGAMI Bot Key:")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    if data == "codm":
        await query.edit_message_text("📄 CODM TXT\n\nSend your CODM file / details here.", reply_markup=get_panel(user_id))
    elif data == "ml":
        await query.edit_message_text("📄 ML TXT\n\nSend your ML file / details here.", reply_markup=get_panel(user_id))
    elif data == "redeem":
        await query.edit_message_text("Enter YAGAMI Bot Key:")
    elif data == "stats":
        await query.edit_message_text(f"📊 MY STATISTICS\n\nUser ID: {user_id}\nStatus: Active\nKeys Left: {len(keys)}", reply_markup=get_panel(user_id))
    elif data == "gen":
        if user_id != OWNER_ID:
            await query.edit_message_text("Admin only!")
            return
        key = make_key()
        keys[key] = None
        await query.edit_message_text(f"New Key Generated:\n`{key}`", parse_mode="Markdown", reply_markup=get_panel(user_id))
    elif data == "ulp":
        await query.edit_message_text("🛠 ULP & DUPLICATE REMOVER\n\nSend your file to clean.", reply_markup=get_panel(user_id))
    elif data == "datadome":
        await query.edit_message_text("🛡 DATADOME GENERATOR\n\nComing soon.", reply_markup=get_panel(user_id))

web = Flask(__name__)
@web.route('/')
def home():
    return "Yagami Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    print("Starting Yagami Bot...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
