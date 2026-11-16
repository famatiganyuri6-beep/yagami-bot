import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
ENTRANCE_KEY = "YAGAMI-ENTER"

authorized = set()
user_state = {}

# Folders
os.makedirs("codm", exist_ok=True)
os.makedirs("ml", exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authorized:
        await update.message.reply_text("🔒 This bot is LOCKED.\n\nEnter Entrance Key:")
        return
    keyboard = [
        [InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")],
        [InlineKeyboardButton("🔥 ML TXT", callback_data="ml")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ]
    await update.message.reply_text(
        "👋 Welcome to YAGAMI BOT!\n\nPili ka:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in authorized:
        await query.message.reply_text("🔒 Locked pa. Type mo muna /start at ilagay ang Entrance Key.")
        return

    if query.data == "codm":
        user_state[user_id] = "codm"
        await query.message.reply_text("🎮 CODM TXT\n\nSend mo na yung .txt file mo dito.\nDapat pangalan nya `codm_xxx.txt`")
    elif query.data == "ml":
        user_state[user_id] = "ml"
        await query.message.reply_text("🔥 ML TXT\n\nSend mo na yung .txt file mo dito.\nDapat pangalan nya `ml_xxx.txt`")
    elif query.data == "help":
        await query.message.reply_text(
            "❓ HELP\n\n"
            "1. Type /start\n"
            "2. Ilagay ang Entrance Key: YAGAMI-ENTER\n"
            "3. Pindutin CODM TXT o ML TXT\n"
            "4. Send mo yung .txt file\n\n"
            "Admin lang makakapag-upload."
        )

async def check_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if user_id not in authorized:
        if text == ENTRANCE_KEY:
            authorized.add(user_id)
            keyboard = [
                [InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")],
                [InlineKeyboardButton("🔥 ML TXT", callback_data="ml")],
                [InlineKeyboardButton("❓ Help", callback_data="help")],
            ]
            await update.message.reply_text(
                "✅ Unlocked! Welcome!\n\nPili ka:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text("❌ Wrong Key. Try ulit.\n\nEnter Entrance Key:")
        return

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authorized:
        await update.message.reply_text("🔒 Locked pa. Type /start muna.")
        return
    if user_id not in user_state:
        await update.message.reply_text("Pindutin mo muna CODM TXT o ML TXT bago mag-send ng file.")
        return
    doc = update.message.document
    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("❌ .txt lang pwede.")
        return
    category = user_state[user_id]
    folder = "codm" if category == "codm" else "ml"
    file = await doc.get_file()
    path = os.path.join(folder, doc.file_name)
    await file.download_to_drive(path)
    await update.message.reply_text(f"✅ Saved! {doc.file_name} sa {folder.upper()}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_key))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
