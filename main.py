import os
import threading
from flask import Flask
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN", "")
app = Flask(__name__)

@app.route('/')
def home():
    return "Yagami Bot is alive!"

bot = telebot.TeleBot(TOKEN) if TOKEN else None

if bot:
    @bot.message_handler(commands=['start'])
    def start(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✨ Help", callback_data="help"))
        markup.add(types.InlineKeyboardButton("🎮 Menu", callback_data="menu"))
        markup.add(types.InlineKeyboardButton("👤 About", callback_data="about"))
        bot.reply_to(message, "Yo! Yagami Bot is here! 😎\nPindutin mo yung buttons sa baba!", reply_markup=markup)

    @bot.message_handler(commands=['help'])
    def help_cmd(message):
        bot.reply_to(message, "Commands:\n/start - Start\n/help - Help\n/menu - Menu")

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.data == "help":
            bot.answer_callback_query(call.id, "Help!")
            bot.send_message(call.message.chat.id, "Commands:\n/start - Start\n/help - Help\n/menu - Menu")
        elif call.data == "menu":
            bot.answer_callback_query(call.id, "Menu!")
            bot.send_message(call.message.chat.id, "Menu:\n1. Help\n2. About\n3. Start")
        elif call.data == "about":
            bot.answer_callback_query(call.id, "About!")
            bot.send_message(call.message.chat.id, "Ako si Yagami Bot, gawa ni Yuri! 🔥")

    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
