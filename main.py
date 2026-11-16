import os
import random
import string
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

def make_key():
    date = datetime.now().strftime("%Y%m%d")
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"YAGAMI-CODM-{date}-{rand}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 CODM 20261116", callback_data="codm")]]
    await update.message.reply_text(
        "👋 Welcome to Yagami Bot!\n\nPili ka ng game:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "codm":
        await query.message.reply_text("Gamitin mo /generate para gumawa ng key.\n⚠️ Admin lang ang makaka-generate.")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Sorry, Admin lang ang makaka-generate ng key.")
        return
    key = make_key()
    await update.message.reply_text(f"✅ Owner confirmed!\n\n🎮 CODM 20261116\n🔑 Key: `{key}`\n\nCopy mo yan!", parse_mode="Markdown")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your ID: `{update.effective_user.id}`", parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot started...")
    app.run_polling()
