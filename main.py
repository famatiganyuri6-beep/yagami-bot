import os
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8089763801

# STOCK - LIST, CAN HOLD MULTIPLE FILES FOR BOTH ML AND CODM
stock_files = {"ML": [], "CODM": []}
waiting_upload = {}
keys = {}
authorized_users = set()

def locked_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 REDEEM KEY", callback_data="redeem")]
    ])

def main_menu(user_id):
    buttons = [
        [InlineKeyboardButton("📄 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("📄 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("🔑 REDEEM KEY", callback_data="redeem"), InlineKeyboardButton("📊 MY STATISTICS", callback_data="stats")],
    ]
    if user_id == OWNER_ID:
        buttons.append([InlineKeyboardButton("🛠 GENERATE KEY", callback_data="generate")])
        buttons.append([InlineKeyboardButton("📤 UPLOAD ML TXT", callback_data="upload_ml")])
        buttons.append([InlineKeyboardButton("📤 UPLOAD CODM TXT", callback_data="upload_codm")])
        buttons.append([InlineKeyboardButton("🗑 CLEAR ML STOCK", callback_data="clear_ml")])
        buttons.append([InlineKeyboardButton("🗑 CLEAR CODM STOCK", callback_data="clear_codm")])
        buttons.append([InlineKeyboardButton("🛠 ULP & DUPLICATE REMOVER", callback_data="ulp")])
        buttons.append([InlineKeyboardButton("🛡 DATADOME GENERATOR", callback_data="datadome")])
    return InlineKeyboardMarkup(buttons)

def is_authorized(user_id):
    return user_id == OWNER_ID or user_id in authorized_users

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_authorized(user_id):
        await update.message.reply_text("👋 Welcome to YAGAMI Bot! Choose below:", reply_markup=main_menu(user_id))
    else:
        await update.message.reply_text("🔒 LOCKED!\n\nThis bot is locked. You need an Entrance Key to access the panel.\n\nClick REDEEM KEY and send your key.", reply_markup=locked_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    user_id = query.from_user.id
    data = query.data

    # --- REDEEM IS ALLOWED EVEN IF LOCKED ---
    if data == "redeem":
        await query.edit_message_text("🔑 Send your ENTRANCE KEY here.")
        context.user_data["waiting_key"] = True
        return

    # --- BLOCK ALL OTHER BUTTONS IF NOT AUTHORIZED ---
    if not is_authorized(user_id):
        await query.edit_message_text("🔒 LOCKED!\n\nYou need an Entrance Key first. Click REDEEM KEY.", reply_markup=locked_menu())
        return

    # --- BUYER CLICKS ML / CODM -> SEND ALL FILES IN LIST ---
    if data in ["ml_txt", "codm_txt"]:
        key = "ML" if data == "ml_txt" else "CODM"
        files = stock_files.get(key, [])
        if not files:
            await query.edit_message_text(f"❌ No stock yet for {key} TXT. Please wait for Boss to upload.")
            return
        await query.edit_message_text(f"📄 Sending {len(files)} file(s) of {key}...")
        for file_id in files:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id, caption=f"📄 {key} TXT")
        return

    # --- OWNER UPLOAD ---
    if data in ["upload_ml", "upload_codm"]:
        if user_id != OWNER_ID:
            await query.answer("Admin only!", show_alert=True)
            return
        key = "ML" if data == "upload_ml" else "CODM"
        waiting_upload[user_id] = key
        await query.edit_message_text(f"📤 Send your {key} .txt FILES here. You can send multiple files, they will be added to the list. To delete all, use CLEAR.")
        return

    # --- OWNER CLEAR ---
    if data in ["clear_ml", "clear_codm"]:
        if user_id != OWNER_ID:
            return
        key = "ML" if data == "clear_ml" else "CODM"
        stock_files[key] = []
        await query.edit_message_text(f"🗑 {key} stock cleared. No files left. Upload again.")
        return

    if data == "generate":
        if user_id != OWNER_ID:
            return
        new_key = "YAGAMI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        keys[new_key] = True
        await query.edit_message_text(f"✅ Your New Entrance Key:\n`{new_key}`\n\nGive this to your buyer. They must redeem it to unlock the panel.", parse_mode="Markdown")
        return

    if data == "stats":
        await query.edit_message_text("📊 MY STATISTICS\nNo data yet.")
        return

    if data == "ulp":
        await query.edit_message_text("🧹 ULP & DUPLICATE REMOVER\nSend your .txt file here.")
        return

    if data == "datadome":
        await query.edit_message_text("🛡 DATADOME GENERATOR\nComing soon Boss!")
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # 1. OWNER UPLOAD - APPEND TO LIST, DO NOT REPLACE OLD FILES
    if user_id in waiting_upload and update.message.document:
        key = waiting_upload[user_id]
        stock_files[key].append(update.message.document.file_id)
        total = len(stock_files[key])
        await update.message.reply_text(f"✅ SAVED! Now you have {total} file(s) in {key}. Send another one, it will be added.")
        return

    # 2. REDEEM ENTRANCE KEY
    if context.user_data.get("waiting_key") and update.message.text:
        key = update.message.text.strip()
        if key in keys:
            del keys[key]
            authorized_users.add(user_id)
            context.user_data["waiting_key"] = False
            await update.message.reply_text("✅ KEY ACCEPTED! Panel unlocked!", reply_markup=main_menu(user_id))
        else:
            await update.message.reply_text("❌ Invalid Key. Try again or contact Boss.")
        return

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, handle_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
