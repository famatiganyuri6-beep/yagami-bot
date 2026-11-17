  import asyncio
  import random
  import string
  import os
  import threading
  from flask import Flask
  from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
  from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes


TOKEN = "9073043795:AAHHIqIxc8h7yTE3fACKLO1kSpU6lsfC_NM"
OWNER_ID = 8089763801
keys = {}

def make_key():
    chars = string.ascii_letters + string.digits
    return "YAGAMI-" + "".join(random.choice(chars) for _ in range(12))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("▶ Start", callback_data="start")],[InlineKeyboardButton("ℹ Help", callback_data="help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Hello! I'm Yagami Bot.", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "start":
        await query.edit_message_text("Let's go! Send /start anytime.")
    elif query.data == "help":
        await query.edit_message_text("Just send /start to see the menu again.")

async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Ikaw lang ang owner ang pwede gumawa ng key. Hindi ka allowed.")
        return
    new_key = make_key()
    keys[new_key] = True
    await update.message.reply_text(f"✅ New key created:\n{new_key}", parse_mode="Markdown")

async def mykeys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Owner lang pwede makita ng keys.")
        return
    if not keys:
        await update.message.reply_text("Wala ka pang nagagawang key.")
        return
    await update.message.reply_text("🔑 Mga keys mo:\n\n" + "\n".join(keys.keys()))

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("genkey", genkey))
    app.add_handler(CommandHandler("mykeys", mykeys))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()
    # Fake website para hindi patayin ni Render
web = Flask(__name__)
@web.route('/')
def home():
    return "Yagami Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

    asyncio.run(main())
