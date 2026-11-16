import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "ILAGAY_MO_DITO_YUNG_TOKEN_MO"

BASE = "https://raw.githubusercontent.com/famatiganyuri6-beep/yagami-bot/main"

FILES = {
    "codm_1909_v1": ("CODM 1909 V1", f"{BASE}/Codm_0725_1909.txt"),
    "codm_1909_v2": ("CODM 1909 V2", f"{BASE}/Codm_0725_1909_1.txt"),
    "codm_1908_v1": ("CODM 1908 V1", f"{BASE}/Codm_0725_1908_1.txt"),
    "mix_1908_v1": ("MIX 1908 V1", f"{BASE}/Mix_Codm_0725_1908_1.txt"),
    "mix_1908_v2": ("MIX 1908 V2", f"{BASE}/Mix_Codm_0725_1908.txt"),
    "clean_1": ("CLEAN CODM 1", f"{BASE}/clean_codm_1.txt"),
    "nov16": ("20261116", f"{BASE}/20261116_1.txt"),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("YAGAMIHAXX TXT", callback_data="menu_txt")]]
    await update.message.reply_text("Pili ka:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_txt":
        keyboard = []
        for key, (name, url) in FILES.items():
            keyboard.append([InlineKeyboardButton(name, callback_data=key)])
        keyboard.append([InlineKeyboardButton("⬅ BACK", callback_data="back")])
        await query.edit_message_text("Pili ka ng file:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "back":
        keyboard = [[InlineKeyboardButton("YAGAMIHAXX TXT", callback_data="menu_txt")]]
        await query.edit_message_text("Pili ka:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data in FILES:
        name, url = FILES[data]
        await query.edit_message_text(f"Sin-send ko na {name}... wait lang!")
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                filename = url.split("/")[-1]
                with open(filename, "wb") as f:
                    f.write(r.content)
                await context.bot.send_document(chat_id=query.message.chat_id, document=open(filename, "rb"), filename=filename, caption=f"✅ {name} - by YAGAMIHAXX")
                os.remove(filename)
            else:
                await context.bot.send_message(chat_id=query.message.chat_id, text=f"Error: Hindi mahanap yung file {name}. Code {r.status_code}")
        except Exception as e:
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot is running...")
    app.run_polling()
