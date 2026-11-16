import os
import threading
from flask import Flask
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN", "")
ENTRANCE_KEY = "YAGAMIOWNBOT+7914&"
AUTHORIZED = set()

app = Flask(__name__)

@app.route('/')
def home():
    return "Yagami Bot is alive!"

bot = telebot.TeleBot(TOKEN) if TOKEN else None

def show_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📁 Files", callback_data="files"))
    markup.add(types.InlineKeyboardButton("❓ Help", callback_data="help"))
    markup.add(types.InlineKeyboardButton("ℹ️ About", callback_data="about"))
    bot.send_message(chat_id, "Welcome to Yagami Bot. What do you want?", reply_markup=markup)

if bot:
    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.from_user.id
        if user_id in AUTHORIZED:
            show_menu(message.chat.id)
        else:
            bot.reply_to(message, "🔒 Enter your key:")

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.from_user.id not in AUTHORIZED:
            bot.answer_callback_query(call.id, "Please enter your key first!")
            return
        if call.data == "files":
            bot.answer_callback_query(call.id, "Files")
            try:
                with open("clean_codm_1.txt", "rb") as f:
                    bot.send_document(call.message.chat.id, f)
            except Exception as e:
                bot.send_message(call.message.chat.id, f"No file found: {e}")
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
        user_id = message.from_user.id
        if user_id in AUTHORIZED:
            return
        if message.text.strip() == ENTRANCE_KEY:
            AUTHORIZED.add(user_id)
            bot.reply_to(message, "✅ Key accepted! Welcome!")
            show_menu(message.chat.id)
        else:
            bot.reply_to(message, "❌ Wrong key. Please try again:")

    def run_bot():
        bot.infinity_polling()

    threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
