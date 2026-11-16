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

def is_admin(user_id):
    return user_id == ADMIN_ID

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
    txt += "Choose an option below:"
    await update.message.reply_text(txt, reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back":
        txt = "Welcome to yagami_bot!\n"
        txt += "Choose an option below:"
        await query.edit_message_text(txt, reply_markup=main_menu())
        return

    if data == "games":
        txt = "Games:\n"
        txt += "CODM Tournament\n"
        txt += "Mix Codm\n"
        txt += "Clean Codm"
        await query.edit_message_text(txt, reply_markup=back_btn())
        return

    if data == "register":
        txt = "Register:\n"
        txt += "Send IGN + UID mo."
        await query.edit_message_text(txt, reply_markup=back_btn())
        return

    if data == "tournament":
        txt = "Tournament: CODM 20261116\n"
        txt += "Status: OPEN\n"
        txt += "Good luck!"
        await query.edit_message_text(txt, reply_markup=back_btn())
        return

    if data == "files":
        files = get_txt_files()
        k = []
        for f in files:
            short = f
            if len(f) > 30:
                short = f[:27] + "..."
            btn = InlineKeyboardButton(short, callback_data="getfile_" + f)
            k.append([btn])
        k.append([InlineKeyboardButton("Back", callback_data="back")])
        txt = "Files:\n"
        txt += "Piliin mo file na gusto mo:"
        await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(k))
        return

    if data.startswith("getfile_"):
        filename = data.replace("getfile_", "", 1)
        try:
            f = open(filename, "rb")
            await query.message.reply_document(document=f, filename=filename)
            f.close()
            await query.answer("Na-send ko na!")
        except Exception as e:
            await query.answer("Error!")
        return

    if data == "help":
        txt = "Help:\n"
        txt += "/start - Open menu\n"
        txt += "Files - Makita lahat ng txt"
        await query.edit_message_text(txt, reply_markup=back_btn())
        return

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
