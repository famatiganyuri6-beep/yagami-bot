from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Put your Bot Token from @BotFather here
TOKEN = "9073043795:AAHHIqIxc8h7yTE3fACKLO1kSpU6lsfC_NM"

# Main Menu Keyboard
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("🔥 ML TXT", callback_data="ml_txt")],
        [InlineKeyboardButton("🔑 Generate Key", callback_data="generate_key")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👋 Hello, Welcome to YAGAMI_BOT!\n\nPlease choose an option below:"
    await update.message.reply_text(text, reply_markup=main_menu())

# Button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "codm_txt":
        await query.edit_message_text(
            "🎮 CODM TXT\n\nSend your CODM .txt file here.",
            reply_markup=main_menu()
        )

    elif query.data == "ml_txt":
        await query.edit_message_text(
            "🔥 ML TXT\n\nSend your ML .txt file here.",
            reply_markup=main_menu()
        )

    elif query.data == "generate_key":
        await query.edit_message_text(
            "🔑 Generate Key\n\nPlease contact admin to generate a key.",
            reply_markup=main_menu()
        )

    elif query.data == "help":
        await query.edit_message_text(
            "❓ Help\n\nUse /start to go back to the main menu.\nIf the bot is not responding, please contact admin.",
            reply_markup=main_menu()
        )

# Run bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
print("Bot is running...")
app.run_polling()
