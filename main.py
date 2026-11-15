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
    markup.add(types.InlineKeyboardButton("✨ Help", callback_data="help"))
    markup.add(types.InlineKeyboardButton("🎮 Menu", callback_data="menu"))
    markup.add(types.InlineKeyboardButton("👤 About", callback_data="about"))
    bot.send_message(chat_id, "Yo! Welcome sa Yagami Bot! 😎\nNaka-pasok ka na! Pindutin mo buttons sa baba!", reply_markup=markup)

if bot:
    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.from_user.id
        if user_id in AUTHORIZED:
            show_menu(message.chat.id)
        else:
            bot.reply_to(message, "🔒 ENTRANCE KEY REQUIRED!\n\nPara makapasok, i-type mo yung Entrance Key mo:")

    @bot.message_handler(commands=['help'])
    def help_cmd(message):
        if message.from_user.id not in AUTHORIZED:
            bot.reply_to(message, "🔒 Maglagay ka muna ng Entrance Key! Mag /start ka muna.")
            return
        bot.reply_to(message, "Commands:\n/start - Start\n/help - Help\n/menu - Menu")

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.from_user.id not in AUTHORIZED:
            bot.answer_callback_query(call.id, "Need Entrance Key muna!")
            return
        if call.data == "help":
            bot.answer_callback_query(call.id, "Help!")
            bot.send_message(call.message.chat.id, "Commands:\n/start - Start\n/help - Help\n/menu - Menu")
        elif call.data == "menu":
            bot.answer_callback_query(call.id, "Menu!")
            bot.send_message(call.message.chat.id, "Menu:\n1. Help\n2. About\n3. Start")
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
            bot.reply_to(message, "❌ MALI YUNG KEY!\nTry mo ulit! Mag /start ka at i-type yung tamang key.")

    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
