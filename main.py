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

# ITO YUNG 5 FILES MO
FILES = [
    "Codm_0725_1909_1.txt",
    "Codm_0725_1909.txt",
    "Codm_0725_1908_1.txt",
    "Mix_Codm_0725_1908.txt",
    "Mix_Codm_0725_1908_1.txt",
]

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

def show_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📁 Files", callback_data="files"))
    markup.add(types.InlineKeyboardButton("❓ Help", callback_data="help"))
    markup.add(types.InlineKeyboardButton("ℹ️ About", callback_data="about"))
    bot.send_message(chat_id, "Welcome to Yagami Bot. What do you want?", reply_markup=markup)

def show_files(chat_id):
    markup = types.InlineKeyboardMarkup()
    for f in FILES:
        markup.add(types.InlineKeyboardButton(f"📄 {f}", callback_data=f"getfile:{f}"))
    markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="back"))
    bot.send_message(chat_id, "📁 Choose a file:", reply_markup=markup)

if bot:
    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(message, "🔒 Enter your key:")

    @bot.message_handler(commands=['genkey'])
    def genkey(message):
        if message.from_user.id not in ADMIN_IDS:
            bot.reply_to(message, "❌ Only admin can generate keys.")
            return
        new_key = generate_key()
        bot.reply_to(message, f"✅ New key generated:\n`{new_key}`\n\nSend this to your buyer. This key never expires.", parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.data == "files":
            bot.answer_callback_query(call.id, "Files")
            show_files(call.message.chat.id)
        elif call.data.startswith("getfile:"):
            filename = call.data.split("getfile:")[1]
            bot.answer_callback_query(call.id, filename)
            try:
                with open(filename, "rb") as f:
                    bot.send_document(call.message.chat.id, f)
            except Exception as e:
                bot.send_message(call.message.chat.id, f"No file found: {e}\nMake sure {filename} is uploaded to GitHub.")
        elif call.data == "back":
            bot.answer_callback_query(call.id, "Back")
            show_menu(call.message.chat.id)
        elif call.data == "help":
            bot.answer_callback_query(call.id, "Help")
            bot.send_message(call.message.chat.id, "Type /start to begin. You need a key to enter.")
        elif call.data == "about":
            bot.answer_callback_query(call.id, "About")
            bot.send_message(call.message.chat.id, "Yagami Bot - Private bot protected by a key.")

    @bot.message_handler(func=lambda m: True)
    def check_key(message):
        if message.text.startswith('/'):
            return
        key = message.text.strip()
        user_id = message.from_user.id
        if key == MASTER_KEY:
            ADMIN_IDS.add(user_id)
            bot.reply_to(message, "✅ Key accepted! Welcome Admin!")
            show_menu(message.chat.id)
        elif key in VALID_KEYS:
            bot.reply_to(message, "✅ Key accepted! Welcome!")
            show_menu(message.chat.id)
        else:
            bot.reply_to(message, "❌ Wrong key. Please try again:")

    def run_bot():
        bot.infinity_polling()

    threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
