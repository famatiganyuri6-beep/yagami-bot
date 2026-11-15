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
    markup.add(types.InlineKeyboardButton("📁 GET FILES", callback_data="files"))
    markup.add(types.InlineKeyboardButton("✨ Help", callback_data="help"))
    markup.add(types.InlineKeyboardButton("👤 About", callback_data="about"))
    bot.send_message(chat_id, "Yo! Welcome sa Yagami Bot! 😎\nNaka-pasok ka na! Pindutin mo sa baba para makuha yung files!", reply_markup=markup)

if bot:
    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.from_user.id
        if user_id in AUTHORIZED:
            show_menu(message.chat.id)
        else:
            bot.reply_to(message, "🔒 ENTRANCE KEY REQUIRED!\n\nPara makapasok, i-type mo yung Entrance Key mo:")

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.from_user.id not in AUTHORIZED:
            bot.answer_callback_query(call.id, "Need Entrance Key muna!")
            return
        if call.data == "files":
            bot.answer_callback_query(call.id, "Sending files...")
            try:
                # Ipapadala yung file mo
                with open("clean_codm_1.txt", "rb") as f:
                    bot.send_document(call.message.chat.id, f, caption="Eto na yung file mo! 🔥\nGaling kay YAGAMIHAXX!")
            except Exception as e:
                bot.send_message(call.message.chat.id, "Wala pa yung file sa GitHub! I-upload mo muna yung clean_codm_1.txt!")
        elif call.data == "help":
            bot.answer_callback_query(call.id, "Help!")
            bot.send_message(call.message.chat.id, "Pindutin mo 📁 GET FILES para makuha yung files!")
        elif call.data == "about":
            bot.answer_callback_query(call.id, "About!")
            bot.send_message(call.message.chat.id, "Ako si Yagami Bot, gawa ni Yuri! 🔥")

    @bot.message_handler(func=lambda m: True)
    def check_key(message):
        if message.text.startswith('/'):
            return
        user_id = message.from_user.id
        if user_id in AUTHORIZED:
            return
        if message.text.strip() == ENTRANCE_KEY:
            AUTHORIZED.add(user_id)
            bot.reply_to(message, "✅ TAMA! WELCOME! 🔥")
            show_menu(message.chat.id)
        else:
            bot.reply_to(message, "❌ MALI YUNG KEY!\nTry mo ulit!")

    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
