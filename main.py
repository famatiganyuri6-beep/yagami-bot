import os
import glob
from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

players = {}
keys = {}
used_keys = set()

def is_admin(uid):
    return uid == ADMIN_ID

def get_txt_files():
    files = glob.glob("*.txt")
    files = [f for f in files if f != "requirements.txt"]
    return sorted(files)

def main_menu():
    k = []
    k.append([InlineKeyboardButton("Games", callback_data="games")])
    k.append([InlineKeyboardButton("Register", callback_data="register")])
    k.append([InlineKeyboardButton("Tournament", callback_data="tournament")])
    k.append([InlineKeyboardButton("Files", callback_data="files")])
    k.append([InlineKeyboardButton("Help", callback_data="help")])
    return InlineKeyboardMarkup(k)

def back_btn():
    k = []
    k.append([InlineKeyboardButton("Back", callback_data="back")])
    return InlineKeyboardMarkup(k)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = "Welcome to yagami_bot!\n"
    txt += "Choose an option below:\n"
    txt += "Or type /register <IGN>"
    await update.message.reply_text(txt, reply_markup=main_menu())

async def register_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        txt = "Register CODM\n\n"
        txt += "Type: /register <Your IGN>\n"
        txt += "Example: /register Yagami"
        await update.message.reply_text(txt)
        return
    ign = " ".join(context.args)
    uid = update.effective_user.id
    players[uid] = ign
    await update.message.reply_text("Registered: " + ign)

async def redeem_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Type: /redeem <KEY>")
        return
    key = context.args[0]
    uid = update.effective_user.id
    if key in used_keys:
        await update.message.reply_text("Key already used!")
        return
    used_keys.add(key)
    ign = players.get(uid, "Unknown")
    txt = "Key Redeemed Successfully!\n\n"
    txt += "Key: " + key + "\n"
    txt += "Player: " + ign + "\n\n"
    txt += "You now have access!"
    await update.message.reply_text(txt)

async def tournament_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = "CODM 20261116 Tournament\n\n"
    txt += "Mode: Battle Royale / Multiplayer\n"
    txt += "Prize: TBA\n"
    txt += "Status: Registration Open\n\n"
    txt += "Registered Players: " + str(len(players)) + "\n\n"
    txt += "Type /register <IGN> to join!"
    await update.message.reply_text(txt)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back":
        txt = "Welcome to yagami_bot!\nChoose an option below:"
        await query.edit_message_text(txt, reply_markup=main_menu())
        return

    if data == "games":
        txt = "Games:\nCODM Tournament\nMix Codm\nClean Codm"
        await query.edit_message_text(txt, reply_markup=back_btn())
        return

    if data == "register":
        txt = "Register CODM\n\nType: /register <Your IGN>\nExample: /register Yagami"
        await query.edit_message_text(txt, reply_markup=back_btn())
        return

    if data == "tournament":
        txt = "CODM 20261116 Tournament\nStatus: Registration Open\nPlayers: " + str(len(players))
        await query.edit_message_text(txt, reply_markup=back_btn())
        return

    if data == "files":
        files = get_txt_files()
        k = []
        for f in files:
            short = f
            if len(f) > 30:
                short = f[:27] + "..."
            k.append([InlineKeyboardButton(short, callback_data="getfile_" + f)])
        k.append([InlineKeyboardButton("Back", callback_data="back")])
        txt = "Files:\nPiliin mo file na gusto mo:"
        await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(k))
        return

    if data.startswith("getfile_"):
        filename = data.replace("getfile_", "", 1)
        try:
            f = open(filename, "rb")
            await query.message.reply_document(document=f, filename=filename)
            f.close()
            await query.answer("Na-send ko na!")
        except Exception:
            await query.answer("Error!")
        return

    if data == "help":
        txt = "Help:\n/start - Menu\n/register <IGN>\n/redeem <KEY>\n/tournament"
        await query.edit_message_text(txt, reply_markup=back_btn())
        return

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register_cmd))
    app.add_handler(CommandHandler("redeem", redeem_cmd))
    app.add_handler(CommandHandler("tournament", tournament_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
