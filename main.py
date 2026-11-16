import os
import asyncio
import random
import string
import glob
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Get Token and Admin ID from Render
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# Storage
players = {}
keys = {}
used_keys = set()

# Check if user is admin
def is_admin(user_id):
    return user_id == ADMIN_ID

# Get all .txt files in same folder
def get_txt_files():
    files = glob.glob("*.txt")
    # Wag isama requirements.txt
    files = [f for f in files if f != "requirements.txt"]
    return sorted(files)

# Main Menu Keyboard
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 Games", callback_data="games")],
        [InlineKeyboardButton("📋 Register", callback_data="register")],
        [InlineKeyboardButton("🏆 Tournament", callback_data="tournament")],
        [InlineKeyboardButton("📁 Files", callback_data="files")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Welcome to yagami_bot! 👋\n\n"
        "🎮 CODM 20261116 Tournament Bot\n"
        "I am online and ready!\n"
        "Choose an option below:"
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu())

# Button Handler - LAHAT NG BUTTON DITO
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # BACK TO MENU
    if data == "back":
        await query.edit_message_text(
            "Welcome to yagami_bot! 👋\n\n"
            "🎮 CODM 20261116 Tournament Bot\n"
            "I am online and ready!\n"
            "Choose an option below:",
            reply_markup=main_menu()
        )
        return

    # GAMES
    if data == "games":
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
        await query.edit_message_text(
            "🎮 Games:\n\n"
            "• CODM Tournament\n"
            "• Mix Codm\n"
            "• Clean Codm\n\n"
            "Piliin mo sa Files yung account na gusto mo.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # REGISTER
    if data == "register":
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
        await query.edit_message_text(
            "📋 Register:\n\n"
            "Send mo yung IGN + UID
