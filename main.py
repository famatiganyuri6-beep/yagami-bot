import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Get Token from Render Environment
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# Store registered players
players = {}

# Start Command - Welcome Message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Games", callback_data="games")],
        [InlineKeyboardButton("📋 Register CODM", callback_data="register")],
        [InlineKeyboardButton("🏆 Tournament", callback_data="tournament")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "Welcome to yagami_bot! 👋\n\n"
        "🎮 CODM 20261116 Tournament Bot\n\n"
        "I am online and ready!\n"
        "Choose an option below:"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ Help - yagami_bot Commands:\n\n"
        "/start - Show main menu\n"
        "/games - Show games list\n"
        "/register <Your IGN> - Register for CODM\n"
        "/tournament - Show tournament info\n"
        "/players - Show registered players\n"
        "/help - Show this help"
    )
    await update.message.reply_text(help_text)

# Games Command
async def games_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    games_text = (
        "🎮 Games Available:\n\n"
        "1. CODM - Battle Royale\n"
        "2. CODM - Multiplayer 5v5\n"
        "3. CODM - 1v1 Duel\n"
        "4. CODM - S&D Tournament\n\n"
        "Type /register <IGN> to join!"
    )
    await update.message.reply_text(games_text)

# Register Command
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Please type: /register <Your IGN>\nExample: /register Yagami")
        return
    ign = " ".join(context.args)
    players[user.id] = {"name": user.first_name, "ign": ign, "username": user.username}
    await update.message.reply_text(f"✅ Registered Successfully!\n\nPlayer: {user.first_name}\nIGN: {ign}\n\nWelcome to yagami_bot Tournament!")

# Tournament Command
async def tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tournament_text = (
        "🏆 CODM 20261116 Tournament\n\n"
        "Mode: Battle Royale / Multiplayer\n"
        "Prize: TBA\n"
        "Status: Registration Open\n\n"
        f"Registered Players: {len(players)}\n\n"
        "Type /register <IGN> to join!"
    )
    await update.message.reply_text(tournament_text)

# Players List Command
async def players_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not players:
        await update.message.reply_text("No players registered yet.\nType /register <IGN> to be first!")
        return
    text = "👥 Registered Players:\n\n"
    for i, p in enumerate(players.values(), 1):
        text += f"{i}. {p['ign']} - {p['name']}\n"
    await update.message.reply_text(text)

# Button Click Handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "games":
        await query.edit_message_text("🎮 Games Available:\n\n1. CODM - Battle Royale\n2. CODM - Multiplayer 5v5\n3. CODM - 1v1 Duel\n4. CODM - S&D Tournament\n\nType /register <IGN> to join!")
    elif query.data == "register":
        await query.edit_message_text("📋 Register CODM\n\nType: /register <Your IGN>\nExample: /register Yagami")
    elif query.data == "tournament":
        await query.edit_message_text(f"🏆 CODM 20261116 Tournament\n\nMode: Battle Royale / Multiplayer\nStatus: Registration Open\nRegistered Players: {len(players)}\n\nType /register <IGN> to join!")
    elif query.data == "help":
        await query.edit_message_text("❓ Help:\n\n/start - Main menu\n/games - Games list\n/register <IGN> - Register\n/tournament - Tournament info\n/players - Players list\n/help - Help")

# Main Function
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("games", games_command))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("tournament", tournament))
    app.add_handler(CommandHandler("players", players_command))
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot started...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
