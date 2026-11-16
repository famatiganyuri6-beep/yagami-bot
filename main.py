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
            seen = set()
            cleaned = []
            removed = 0
            for line in lines:
                line_strip = line.strip()
                if line_strip not in seen and line_strip != "":
                    seen.add(line_strip)
                    cleaned.append(line_strip)
                else:
                    removed += 1
            out_path = f"cleaned_{message.document.file_name}"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(cleaned))
            with open(out_path, "rb") as f:
                bot.send_document(message.chat.id, f, caption=f"✅ Done!\nOriginal: {len(lines)} lines\nCleaned: {len(cleaned)} lines\nRemoved: {removed} duplicates")
            os.remove(out_path)
        except Exception as e:
            bot.send_message(message.chat.id, f"Error: {e}\nPlease send a .txt file.")

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.data.startswith("getfile:"):
            filename = call.data.split("getfile:")[1]
            bot.answer_callback_query(call.id, filename)
            try:
                with open(filename, "rb") as f:
                    bot.send_document(call.message.chat.id, f, caption=f"📄 {filename}")
            except Exception as e:
                bot.send_message(call.message.chat.id, f"No file found: {e}")

    @bot.message_handler(func=lambda m: True)
    def menu_handler(message):
        text = message.text.strip()
        user_id = message.from_user.id
        if text == "🔑 REDEEM KEY":
            bot.send_message(message.chat.id, "🔒 Please send your key here:")
            return
        if text == "🎮 CODM FILES":
            show_files_inline(message.chat.id, "CODM")
            return
        if text == "🎮 ML FILES":
            show_files_inline(message.chat.id, "ML")
            return
        if text == "🛠️ ULP & DUPLICATE REMOVER":
            bot.send_message(message.chat.id, "🛠️ Send your .txt file with duplicates here.")
            return
        if text == "📢 CHANNEL":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📢 JOIN CHANNEL", url=CHANNEL_LINK))
            bot.send_message(message.chat.id, "📢 Join our official channel for updates and new files!", reply_markup=markup)
            return
        if text == "ℹ️ ABOUT":
            bot.send_message(message.chat.id, "YAGAMI BOT - Private bot.\nCODM & ML Files | ULP Cleaner\nOwner: @yagami\nChannel: https://t.me/channelseiei")
            return
        if text.startswith('/'):
            return
        if text == MASTER_KEY:
            ADMIN_IDS.add(user_id)
            bot.reply_to(message, "✅ Key accepted! Welcome Admin!", reply_markup=main_menu())
        elif text in VALID_KEYS:
            bot.reply_to(message, "✅ Key accepted! Welcome!", reply_markup=main_menu())
        else:
            bot.reply_to(message, "❌ Wrong key. Tap 🔑 REDEEM KEY again and try again.", reply_markup=main_menu())

    def run_bot():
        bot.infinity_polling()

    threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))))
