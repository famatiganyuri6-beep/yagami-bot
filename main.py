import os
import threading
import random
import string
from flask import Flask
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN", "")
MASTER_KEY = "YAGAMIOWNBOT+7914&"
VALID_KEYS = set([MASTER_KEY])
ADMIN_IDS = set()
CHANNEL_LINK = "https://t.me/channelseiei"

CATEGORIES = {
    "CODM": [
        ("CODM 1909 - V1", "Codm_0725_1909_1.txt"),
        ("CODM 1909 - V2", "Codm_0725_1909.txt"),
        ("CODM 1908 - V1", "Codm_0725_1908_1.txt"),
        ("MIX CODM 1908 - V1", "Mix_Codm_0725_1908.txt"),
        ("MIX CODM 1908 - V2", "Mix_Codm_0725_1908_1.txt"),
    ],
    "ML": [
        ("ML UPASS 3K", "Mobile_Legends_upass_3K_1794095825.txt"),
        ("YAGAMI ML", "YAGAMI_ML.txt"),
        ("DEVICE 1000", "device_1000.txt"),
        ("DEVICE 1000 - V2", "device_1000_1.txt"),
    ],
}

app = Flask(__name__)

@app.route('/')
def home():
    return "Yagami Bot is alive!"

bot = telebot.TeleBot(TOKEN) if TOKEN else None

def generate_key():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    new_key = f"YAGAMI-{code[:4]}-{code[4:]}"
    VALID_KEYS.add(new_key)
    return new_key

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🔑 REDEEM KEY"),
        types.KeyboardButton("🎮 CODM FILES")
    )
    markup.add(
        types.KeyboardButton("🎮 ML FILES"),
        types.KeyboardButton("🛠️ ULP & DUPLICATE REMOVER")
    )
    markup.add(
        types.KeyboardButton("📢 CHANNEL"),
        types.KeyboardButton("ℹ️ ABOUT")
    )
    return markup

def show_files_inline(chat_id, category):
    files = CATEGORIES.get(category, [])
    markup = types.InlineKeyboardMarkup()
    for title, filename in files:
        markup.add(types.InlineKeyboardButton(f"📄 {title}", callback_data=f"getfile:{filename}"))
    bot.send_message(chat_id, f"📁 {category} Files - Choose one:", reply_markup=markup)

if bot:
    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id, "Welcome to YAGAMI BOT 🔥\n\nJust tap a button below to continue.\n\nTo get access, tap 🔑 REDEEM KEY and enter your key.", reply_markup=main_menu())

    @bot.message_handler(commands=['genkey'])
    def genkey(message):
        if message.from_user.id not in ADMIN_IDS:
            bot.reply_to(message, "❌ Only admin can generate keys.")
            return
        new_key = generate_key()
        bot.reply_to(message, f"✅ New key generated:\n`{new_key}`", parse_mode="Markdown")

    @bot.message_handler(content_types=['document'])
    def handle_doc(message):
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            text = downloaded.decode('utf-8', errors='ignore')
            lines = text.splitlines()
