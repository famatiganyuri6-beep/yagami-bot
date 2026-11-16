import os
import glob
from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext import ContextTypes
from telegram.ext import filters

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

ENTRANCE_KEY = "YAGAMI-ENTER"

authorized = set()

def main_menu():
    k = []
    k.append([InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")])
    k.append([InlineKeyboardButton("🔥 ML TXT", callback_data="ml")])
    k.append([InlineKeyboardButton("❓ Help", callback_data="help")])
    return InlineKeyboardMarkup(k)

def back_btn():
    k = []
    k.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
    return InlineKeyboardMarkup(k)

def get_files_by_type(game):
    files = glob.glob("*.txt")
    files = [f for f in files if f != "requirements.txt"]
    result = []
    for f in files:
        low = f.lower()
        if game == "codm":
            if "codm" in low or "callofduty" in low or "call-of-duty" in low:
                result.append(f)
        if game == "ml":
            if low.startswith("ml") or "mlbb" in low or "mobilelegends" in low or "mobile-legends" in low:
                result.append(f)
    return sorted(result)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in authorized:
        await update.message.reply_text("Welcome back to yagami_bot!\nChoose an option below:", reply_markup=main_menu())
        return
    await update.message.reply_text("Welcome to yagami_bot!\n\nThis bot is LOCKED.\nEnter Entrance Key to continue:")

async def check_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in authorized:
        return
    text = update.message.text.strip()
    if text == ENTRANCE_KEY:
        authorized.add(uid)
        await update.message.reply_text("Key Accepted! Welcome!", reply_markup=main_menu())
    else:
        await update.message.reply_text("Wrong Key! Try again.\nEnter Entrance Key:")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id not in authorized:
        await query.edit_message_text("Locked! Send Entrance Key first. Type /start")
        return
    data = query.data
    if data == "back":
        await query.edit_message_text("Welcome to yagami_bot!\nChoose an option below:", reply_markup=main_menu())
        return
    if data == "codm":
        files = get_files_by_type("codm")
        if not files:
            await query.edit_message_text("CODM TXT\n\nWala pang CODM file.\nMag-upload ka ng file na may pangalan na:\ncodm_xxx.txt", reply_markup=back_btn())
            return
        k = []
        for f in files:
            short = f
            if len(f) > 30:
                short = f[:27] + "..."
            k.append([InlineKeyboardButton(short, callback_data="getfile_" + f)])
        k.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
        await query.edit_message_text("🎮 CODM TXT\nPiliin mo account:", reply_markup=InlineKeyboardMarkup(k))
        return
    if data == "ml":
        files = get_files_by_type("ml")
        if not files:
            await query.edit_message_text("ML TXT\n\nWala pang ML file.\nMag-upload ka ng file na may pangalan na:\nml_xxx.txt", reply_markup=back_btn())
            return
        k = []
        for f in files:
            short = f
            if len(f) > 30:
                short = f[:27] + "..."
            k.append([InlineKeyboardButton(short, callback_data="getfile_" + f)])
        k.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
        await query.edit_message_text("🔥 ML TXT\nPiliin mo account:", reply_markup=InlineKeyboardMarkup(k))
        return
    if data.startswith("getfile_"):
        filename = data.replace("getfile_", "", 1)
        try:
            f = open(filename, "rb")
            await query.message.reply_document(document=f, filename=filename)
            f.close()
        except Exception:
            await query.answer("Error!")
        return
    if data == "help":
        await query.edit_message_text("Help:\n\n1. Pindutin CODM TXT para sa CODM accounts\n2. Pindutin ML TXT para sa ML accounts\n3. Pindutin yung file para ma-download\n\n/start - Menu", reply_markup=back_btn())
        return

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_key))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
