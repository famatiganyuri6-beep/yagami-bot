 import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Get bot token and admin ID from Render environment variables
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# This runs when user types /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎮 CODM 20261116\n\nWelcome! Bot is online.")

# Main function with proper event loop for Python 3.14
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot started...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
