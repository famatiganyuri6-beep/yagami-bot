import asyncio
import random
import string
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "9073043795:AAHHIqIxc8h7yTE3fACKLO1kSpU6lsfC_NM"
OWNER_ID = 8089763801
keys = {}

def make_key():
    chars = string.ascii_letters + string.digits
    return "YAGAMI-" + "".join(random.choice(chars) for _ in range(12))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yagami Bot is alive! Type /gen to make a key.")

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Owner only!")
        return
    key = make_key()
    keys[key] = None
    await update.message.reply_text(f"New key: {key}")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

web = Flask(__name__)
@web.route('/')
def home():
    return "Yagami Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()
asyncio.run(main())
