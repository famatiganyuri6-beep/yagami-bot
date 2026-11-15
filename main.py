import os
import threading
from flask import Flask
import telebot

TOKEN = os.environ.get("BOT_TOKEN", "")
app = Flask(__name__)

bot = telebot.TeleBot(TOKEN) if TOKEN else None

if bot:
    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(message, "Yo! Yagami is here. 😈 Type /help para makita commands.")

    @bot.message_handler(commands=['help'])
    def help_cmd(message):
        bot.reply_to(message, "Commands:\n/start - Simulan\n/help - Tulong\n/hi - Batiin si Yagami")

    @bot.message_handler(commands=['hi'])
    def hi(message):
        bot.reply_to(message, "Oi! Kamusta ka? Ako si Yagami!")

    @bot.message_handler(func=lambda m: True)
    def echo(message):
        bot.reply_to(message, f"Yagami: Nakuha ko - {message.text}")

@app.route('/')
def home():
    return "Yagami Bot is Alive!"

def run_bot():
    if bot:
        bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
