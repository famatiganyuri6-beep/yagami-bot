import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "ILAGAY_MO_DITO_YUNG_TOKEN_MO")
OWNER_ID = 8089763801 
BASE = "https://raw.githubusercontent.com/famatiganyuri6-beep/yagami-bot/main/"

FILES = {
    "codm_1909_v1": ("CODM 1909 V1", f"{BASE}Codm_0725_1909.txt"),
    "codm_1909_v2": ("CODM 1909 V2", f"{BASE}Codm_0725_1909_v2.txt"),
    "codm_1908_v1": ("CODM 1908 V1", f"{BASE}Codm_0725_1908.txt"),
    "mix_1908_v1": ("MIX 1908 V1", f"{BASE}Mix Codm_0725_1908.txt"),
    "mix_1908_v2": ("MIX 1908 V2", f"{BASE}Mix Codm_0725_1908_v2.txt"),
    "clean_1": ("CLEAN CODM 1", f"{BASE}clean_codm_1.txt"),
    "codm_20261116": ("CODM 20261116", f"{BASE}20261116_1.txt"),
}

# --- PROTECTION: IKAW LANG MAKAKA-GENERATE ---
def is_owner(user_id):
    return user_id == OWNER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=key)] for key, (name, url) in FILES.items()]
    await update.message.reply_text("Pili ka:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data
    name, url = FILES[key]
    r = requests.get(url)
    await query.message.reply_document(document=r.content, filename=f"{name}.txt", caption=name)

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # DITO YUNG PROTECTION MO, HINDI TO MAWAWALA
    if not is_owner(update.message.from_user.id):
        await update.message.reply_text("❌ Ikaw lang ang owner ang pwede mag-generate! Hindi pwede sa iba.")
        return
    await update.message.reply_text("✅ Owner confirmed! Generating key...")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send mo yung key mo:")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("generate", generate))
app.add_handler(CommandHandler("key", generate))
app.add_handler(CommandHandler("redeem", redeem))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
