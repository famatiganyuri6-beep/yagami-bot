import os
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

valid_keys = set()
authorized = set()

def make_key():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return "YAGAMI-" + code

def menu(is_admin):
    if is_admin:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")],
            [InlineKeyboardButton("🔥 ML TXT", callback_data="ml")],
            [InlineKeyboardButton("🔑 Generate Key", callback_data="genkey")],
            [InlineKeyboardButton("❓ Help", callback_data="help")],
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")],
        [InlineKeyboardButton("🔥 ML TXT", callback_data="ml")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid == ADMIN_ID:
        authorized.add(uid)
        await update.message.reply_text("👑 Welcome to YAGAMI BOT, Admin!", reply_markup=menu(True))
        return
    if uid not in authorized:
        await update.message.reply_text("🔒 Welcome to YAGAMI BOT\n\nThis bot is LOCKED.\nPlease enter your Entrance Key:")
        return
    await update.message.reply_text("👋 Welcome to YAGAMI BOT!", reply_markup=menu(False))

async def newkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid != ADMIN_ID:
        await update.message.reply_text("❌ Only Admin can generate keys.")
        return
    key = make_key()
    valid_keys.add(key)
    await update.message.reply_text(f"🔑 New Key:\n\n{key}")

async def codm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in authorized and uid != ADMIN_ID:
        await update.message.reply_text("🔒 Locked. Type /start first.")
        return
    await update.message.reply_text("🎮 CODM TXT\n\nSend your CODM .txt file here.")

async def ml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in authorized and uid != ADMIN_ID:
        await update.message.reply_text("🔒 Locked. Type /start first.")
        return
    await update.message.reply_text("🔥 ML TXT\n\nSend your ML .txt file here.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ HELP\n\n1. Type /start\n2. Enter key\n3. Press CODM TXT or ML TXT")

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    if q.data == "codm":
        await q.message.reply_text("🎮 CODM TXT\n\nSend your CODM .txt file here.")
    elif q.data == "ml":
        await q.message.reply_text("🔥 ML TXT\n\nSend your ML .txt file here.")
    elif q.data == "help":
        await q.message.reply_text("❓ HELP\n\nPress CODM TXT or ML TXT.")
    elif q.data == "genkey":
        if uid != ADMIN_ID:
            await q.message.reply_text("❌ Only Admin can generate keys.")
            return
        key = make_key()
        valid_keys.add(key)
        await q.message.reply_text(f"🔑 New Key:\n\n{key}")

async def check_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    if uid in authorized or uid == ADMIN_ID:
        return
    if text in valid_keys:
        valid_keys.remove(text)
        authorized.add(uid)
        await update.message.reply_text("✅ Key Accepted! Welcome to YAGAMI BOT!", reply_markup=menu(False))
    else:
        await update.message.reply_text("❌ Invalid Key. Try again:")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newkey", newkey))
    app.add_handler(CommandHandler("codm", codm))
    app.add_handler(CommandHandler("ml", ml))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_key))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
