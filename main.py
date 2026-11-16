
import os
import asyncio
import secrets
import string

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Configuration
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# Storage
keys = set()
ok = set()


# Generate entrance key
def mk():
    characters = string.ascii_uppercase + string.digits
    return "YAGAMI-" + "".join(
        secrets.choice(characters) for _ in range(6)
    )


# Check authorization
def authorized(user_id):
    return user_id == ADMIN_ID or user_id in ok


# Main menu
def menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")],
        [InlineKeyboardButton("🔥 ML TXT", callback_data="ml")],
    ]

    if is_admin:
        buttons.append([
            InlineKeyboardButton(
                "🔑 Generate Key",
                callback_data="genkey"
            )
        ])

    buttons.append([
        InlineKeyboardButton("❓ Help", callback_data="help")
    ])

    return InlineKeyboardMarkup(buttons)


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        ok.add(user_id)

        await update.message.reply_text(
            "👑 Welcome to YAGAMI BOT, Admin!",
            reply_markup=menu(True)
        )

    elif user_id not in ok:
        await update.message.reply_text(
            "🔒 Welcome to YAGAMI BOT\n\n"
            "This bot is LOCKED.\n"
            "Please enter your Entrance Key:"
        )

    else:
        await update.message.reply_text(
            "👋 Welcome to YAGAMI BOT!",
            reply_markup=menu(False)
        )


# Generate new key
async def newkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ Only Admin can generate keys."
        )
        return

    key = mk()
    keys.add(key)

    await update.message.reply_text(
        f"🔑 New Key:\n\n{key}"
    )


# CODM command
async def codm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update.effective_user.id):
        await update.message.reply_text("🔒 Access denied.")
        return

    await update.message.reply_text(
        "🎮 CODM TXT\n\nSend your CODM .txt file here."
    )


# ML command
async def ml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update.effective_user.id):
        await update.message.reply_text("🔒 Access denied.")
        return

    await update.message.reply_text(
        "🔥 ML TXT\n\nSend your ML .txt file here."
    )


# Help command
async def hlp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ HELP\n\n"
        "1. Type /start\n"
        "2. Enter your Entrance Key\n"
        "3. Press CODM TXT or ML TXT\n"
        "4. Send your .txt file"
    )


# Button handler
async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not authorized(user_id):
        await query.message.reply_text("🔒 Access denied.")
        return

    if query.data == "codm":
        await query.message.reply_text(
            "🎮 CODM TXT\n\nSend your CODM .txt file here."
        )

    elif query.data == "ml":
        await query.message.reply_text(
            "🔥 ML TXT\n\nSend your ML .txt file here."
        )

    elif query.data == "help":
        await hlp(query, context)

    elif query.data == "genkey":
        if user_id != ADMIN_ID:
            await query.message.reply_text(
                "❌ Only Admin can generate keys."
            )
            return

        key = mk()
        keys.add(key)

        await query.message.reply_text(
            f"🔑 New Key:\n\n{key}"
        )


# Entrance key verification
async def chk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if authorized(user_id):
        return

    if text in keys:
        keys.remove(text)
        ok.add(user_id)

        await update.message.reply_text(
            "✅ Key Accepted! Welcome to YAGAMI BOT!",
            reply_markup=menu(False)
        )

    else:
        await update.message.reply_text(
            "❌ Invalid Key. Try again:"
        )


# TXT file handler
async def handle_document(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if not authorized(user_id):
        await update.message.reply_text("🔒 Access denied.")
        return

    document = update.message.document
    filename = document.file_name or ""

    if not filename.lower().endswith(".txt"):
        await update.message.reply_text(
            "❌ Only .txt files are accepted."
        )
        return

    await update.message.reply_text(
        f"✅ File received successfully!\n\n"
        f"📄 Filename: {filename}\n"
        "Your TXT file has been received."
    )


# Run bot asynchronously
async def run_bot():
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newkey", newkey))
    app.add_handler(CommandHandler("codm", codm))
    app.add_handler(CommandHandler("ml", ml))
    app.add_handler(CommandHandler("help", hlp))

    app.add_handler(CallbackQueryHandler(btn))

    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            handle_document
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chk
        )
    )

    initialized = False
    started = False
    polling = False

    try:
        await app.initialize()
        initialized = True

        await app.start()
        started = True

        await app.updater.start_polling(
            drop_pending_updates=True
        )
        polling = True

        print("YAGAMI BOT is running successfully!")

        await asyncio.Event().wait()

    finally:
        if polling:
            await app.updater.stop()

        if started:
            await app.stop()

        if initialized:
            await app.shutdown()


# Main entry point
def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing in environment variables.")

    if ADMIN_ID == 0:
        raise ValueError("ADMIN_ID is missing in environment variables.")

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
    
