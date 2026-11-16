import os
import asyncio
import random
import string
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

# Start Command
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
        "For Everyone:\n"
        "/start - Show main menu\n"
        "/games - Show games list\n"
        "/register <Your IGN> - Register for CODM\n"
        "/tournament - Show tournament info\n"
        "/players - Show registered players\n"
        "/redeem <KEY> - Redeem a key\n\n"
        "For Admin Only:\n"
        "/genkey - Generate a new key\n"
        "/keys - Show all keys\n"
        "/myid - Show your ID"
    )
    await update.message.reply_text(help_text)

# Show My ID - So you can check your Admin ID
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    status = "✅ YOU ARE ADMIN" if is_admin(user_id) else "❌ NOT ADMIN"
    await update.message.reply_text(f"Your ID: {user_id}\nStatus: {status}\nAdmin ID in system: {ADMIN_ID}")

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

# Players List
async def players_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not players:
        await update.message.reply_text("No players registered yet.\nType /register <IGN> to be first!")
        return
    text = "👥 Registered Players:\n\n"
    for i, p in enumerate(players.values(), 1):
        text += f"{i}. {p['ign']} - {p['name']}\n"
    await update.message.reply_text(text)

# Generate Key - ADMIN ONLY
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Access Denied!\nOnly Admin can generate keys!")
        return
    # Generate random key
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    new_key = f"YAGAMI-{code}"
    keys[new_key] = {"created_by": user_id, "used": False, "used_by": None}
    await update.message.reply_text(f"🔑 New Key Generated!\n\nKey: `{new_key}`\n\nSend this key to player. They can redeem with:\n/redeem {new_key}", parse_mode="Markdown")

# Show All Keys - ADMIN ONLY
async def keys_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Access Denied!\nOnly Admin can view keys!")
        return
    if not keys:
        await update.message.reply_text("No keys generated yet.\nType /genkey to create one.")
        return
    text = "🔑 All Keys:\n\n"
    for k, v in keys.items():
        status = "✅ USED" if v["used"] else "🟢 UNUSED"
        text += f"{k} - {status}\n"
    await update.message.reply_text(text)

# Redeem Key - For Players
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Please type: /redeem <KEY>\nExample: /redeem YAGAMI-ABC123")
        return
    key_input = context.args[0].upper()
    if key_input in used_keys:
        await update.message.reply_text("❌ This key is already used!")
        return
    if key_input not in keys:
        await update.message.reply_text("❌ Invalid key! Please check and try again.")
        return
    keys[key_input]["used"] = True
    keys[key_input]["used_by"] = user.id
    used_keys.add(key_input)
    await update.message.reply_text(f"✅ Key Redeemed Successfully!\n\nKey: {key_input}\nPlayer: {user.first_name}\n\nYou now have access!")

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
        await query.edit_message_text("❓ Help:\n\n/start - Main menu\n/games - Games list\n/register <IGN> - Register\n/tournament - Tournament info\n/players - Players list\n/redeem <KEY> - Redeem key\n/help - Help")

# Main Function
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("games", games_command))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("tournament", tournament))
    app.add_handler(CommandHandler("players", players_command))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("genkey", genkey))
    app.add_handler(CommandHandler("keys", keys_command))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot started...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
