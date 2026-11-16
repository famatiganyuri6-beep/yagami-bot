import telebot
import os
import random
import string
from telebot import types
from flask import Flask
import threading

TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 8089763801
MASTER_KEY = "YAGAMIOWNBOT+7914&"
bot = telebot.TeleBot(TOKEN)
keys_db = {}

CATEGORIES = {
    "CODM": ["CODM 1909 V1", "CODM 1909 V2", "CODM 1908", "MIX CODM"],
    "ML": ["ML FILE 1", "ML FILE 2"],
    "ULP": ["ULP FILE"],
}

def generate_key():
    return "YAGAMI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("🔑 REDEEM KEY", "🎮 CODM")
    markup.add("🎮 ML", "🛠️ ULP")
    markup.add("📢 CHANNEL", "ℹ️ ABOUT")
    return markup

def category_keyboard(category):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    for title in CATEGORIES.get(category, []):
        markup.add(title)
    markup.add("⬅️ BACK")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Yagami Bot is Online! What do you want?", reply_markup=main_keyboard())

@bot.message_handler(commands=['genkey'])
def genkey(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Only Owner can generate keys.")
        return
    new_key = generate_key()
    keys_db[new_key] = False
    bot.reply_to(message, f"✅ New Key:\n`{new_key}`", parse_mode="Markdown")

@bot.message_handler(commands=['redeem'])
def redeem(message):
    try:
        key = message.text.split()[1]
        if key == MASTER_KEY or (key in keys_db and not keys_db[key]):
            if key in keys_db:
                keys_db[key] = True
            bot.reply_to(message, "✅ Key Accepted! Premium Unlocked.", reply_markup=main_keyboard())
        else:
            bot.reply_to(message, "❌ Invalid or Already Used.")
    except:
        bot.reply_to(message, "Use: /redeem YAGAMI-XXXX")

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    text = message.text
    if text == "🔑 REDEEM KEY":
        bot.send_message(message.chat.id, "Send: /redeem YAGAMI-XXXX", reply_markup=main_keyboard())
    elif text == "🎮 CODM":
        bot.send_message(message.chat.id, "📂 CODM Files:", reply_markup=category_keyboard("CODM"))
    elif text == "🎮 ML":
        bot.send_message(message.chat.id, "📂 ML Files:", reply_markup=category_keyboard("ML"))
    elif text == "🛠️ ULP":
        bot.send_message(message.chat.id, "📂 ULP Files:", reply_markup=category_keyboard("ULP"))
    elif text == "📢 CHANNEL":
        bot.send_message(message.chat.id, "Channel: https://t.me/yagami", reply_markup=main_keyboard())
    elif text == "ℹ️ ABOUT":
        bot.send_message(message.chat.id, "Yagami Bot by Owner", reply_markup=main_keyboard())
    elif text == "⬅️ BACK":
        bot.send_message(message.chat.id, "Choose:", reply_markup=main_keyboard())
    elif text in ["CODM 1909 V1", "CODM 1909 V2", "CODM 1908", "MIX CODM", "ML FILE 1", "ML FILE 2", "ULP FILE"]:
        bot.send_message(message.chat.id, f"You selected {text}. File is locked. Redeem a key first.", reply_markup=main_keyboard())

# --- PAMPAGISING PARA HINDI MATULOG SA RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Yagami Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

print("Bot is running...")
bot.polling(none_stop=True)
