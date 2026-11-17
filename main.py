import os
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8089763801

# STOCK - Dito naka-save yung FILES mo, 1 file lang per button
stock_files = {"ML": None, "CODM": None}
waiting_upload = {}
keys = {}
user_keys = {}

def main_menu(user_id):
    buttons = [
        [InlineKeyboardButton("📄 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("📄 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("🔑 REDEEM KEY", callback_data="redeem"), InlineKeyboardButton("📊 MY STATISTICS", callback_data="stats")],
    ]
    if user_id == OWNER_ID:
        buttons.append([InlineKeyboardButton("🛠 GENERATE KEY", callback_data="generate")])
        buttons.append([InlineKeyboardButton("📤 UPLOAD ML TXT", callback_data="upload_ml")])
        buttons.append([InlineKeyboardButton("📤 UPLOAD CODM TXT", callback_data="upload_codm")])
        buttons.append([InlineKeyboardButton("🛠 ULP & DUPLICATE REMOVER", callback_data="ulp")])
        buttons.append([InlineKeyboardButton("🛡 DATADOME GENERATOR", callback_data="datadome")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("👋 Welcome to YAGAMI Bot! Choose below:", reply_markup=main_menu(user_id))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # --- BUYER PININDOT ML / CODM -> LABAS YUNG FILE ---
    if data in ["ml_txt", "codm_txt"]:
        key = "ML" if data == "ml_txt" else "CODM"
        file_id = stock_files.get(key)
        if not file_id:
            await query.edit_message_text(f"❌ Wala pang laman yung {key} TXT. Wait mo si Boss mag-upload.")
            return
        await context.bot.send_document(chat_id=query.message.chat_id, document=file_id, caption=f"📄 Ito na yung {key} TXT mo!")
        return

    # --- OWNER PININDOT UPLOAD ---
    if data in ["upload_ml", "upload_codm"]:
        if user_id != OWNER_ID:
            await query.answer("Admin only!", show_alert=True)
            return
        key = "ML" if data == "upload_ml" else "CODM"
        waiting_upload[user_id] = key
        await query.edit_message_text(f"📤 Send mo na yung {key} .txt FILE mo dito. Pag nag-send ka ng bago, mapapalitan yung luma.")
        return

    if data == "generate":
        if user_id != OWNER_ID:
            return
        new_key = "YAGAMI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        keys[new_key] = True
        await query.edit_message_text(f"✅ New Key mo boss:\n`{new_key}`", parse_mode="Markdown")
        return

    if data == "redeem":
        await query.edit_message_text("🔑 Send mo yung KEY mo dito.")
        context.user_data["waiting_key"] = True
        return

    if data == "stats":
        await query.edit_message_text("📊 MY STATISTICS\nWala pang data.")
        return

    if data == "ulp":
        await query.edit_message_text("🧹 ULP & DUPLICATE REMOVER\nSend mo yung .txt file mo dito.")
        return

    if data == "datadome":
        await query.edit_message_text("🛡 DATADOME GENERATOR\nSoon boss!")
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # 1. KUNG NAG-A-UPLOAD SI OWNER NG FILE
    if user_id in waiting_upload and update.message.document:
        key = waiting_upload.pop(user_id)
        stock_files[key] = update.message.document.file_id
        await update.message.reply_text(f"✅ NA-SAVE NA! Pag may nag-click ng {key} TXT, ito na yung FILE na lalabas.")
        return

    # 2. KUNG NAGRE-REDEEM SI BUYER
    if context.user_data.get("waiting_key") and update.message.text:
        key = update.message.text.strip()
        if key in keys:
            del keys[key]
            user_keys[user_id] = key
            context.user_data["waiting_key"] = False
            await update.message.reply_text("✅ KEY ACCEPTED!", reply_markup=main_menu(user_id))
        else:
            await update.message.reply_text("❌ Invalid Key.")
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
