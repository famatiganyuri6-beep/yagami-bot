import telebot
import os
import random
import json
from telebot import types
from flask import Flask
import threading

TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 8089763801
MASTER_KEY = "YAGAMIOWNBOT+7914&"
bot = telebot.TeleBot(TOKEN)

# --- FIX: SAVE PREMIUM SA FILE, HINDI SA MEMORY LANG ---
keys_db = {}
premium_users = set()

# Load saved premium users pag nag-restart
if os.path.exists("premium.json"):
    try:
        with open("premium.json", "r") as f:
            data = json.load(f)
            premium_users = set(data.get("premium_users", []))
            keys_db = data.get("keys_db", {})
    except:
        pass

def save_data():
    with open("premium.json", "w") as f:
        json.dump({"premium_users": list(premium_users), "keys_db": keys_db}, f)

CATEGORIES = {
    "CODM": ["CODM 1909 V1", "CODM 1909 V2"],
    "ML": ["ML FILE 1", "ML FILE 2"],
    "ULP": ["ULP FILE"],
}

def generate_key():
    return "YAGAMI-" + ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔑 REDEEM KEY", "🎮 CODM")
    markup.add("🎮 ML", "🛠️ ULP")
    markup.add("📣 CHANNEL", "ℹ️ ABOUT")
    return markup

def category_keyboard(category):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
        bot.reply_to(message, "❌ Only Owner can generate keys!")
        return
    new_key = generate_key()
    keys_db[new_key] = False
    save_data()
    bot.reply_to(message, f"✅ New Key: `{new_key}`", parse_mode="Markdown")

@bot.message_handler(commands=['redeem'])
def redeem(message):
    try:
        key = message.text.split()[1]
        user_id = message.from_user.id
        # Check Master Key or Generated Key
        if key == MASTER_KEY:
            premium_users.add(user_id)
            save_data()
            bot.reply_to(message, "✅ Key Accepted! Premium Unlocked.")
        elif key in keys_db and keys_db[key] == False:
            keys_db[key] = True
            premium_users.add(user_id)
            save_data()
            bot.reply_to(message, "✅ Key Accepted! Premium Unlocked.")
        elif key in keys_db and keys_db[key] == True:
            bot.reply_to(message, "❌ Key already used!")
        else:
            bot.reply_to(message, "❌ Invalid Key!")
    except:
        bot.reply_to(message, "Use: /redeem YOUR_KEY")

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    text = message.text
    user_id = message.from_user.id
    if text == "🔑 REDEEM KEY":
        bot.send_message(message.chat.id, "Send: /redeem YOUR_KEY")
    elif text == "🎮 CODM":
        bot.send_message(message.chat.id, "Choose CODM File:", reply_markup=category_keyboard("CODM"))
    elif text == "🎮 ML":
        bot.send_message(message.chat.id, "Choose ML File:", reply_markup=category_keyboard("ML"))
    elif text == "🛠️ ULP":
        bot.send_message(message.chat.id, "Choose ULP File:", reply_markup=category_keyboard("ULP"))
    elif text == "📣 CHANNEL":
        bot.send_message(message.chat.id, "Join our channel: @yourchannel")
    elif text == "ℹ️ ABOUT":
        bot.send_message(message.chat.id, "Yagami Bot - Premium Files")
    elif text == "⬅️ BACK":
        bot.send_message(message.chat.id, "Back to main:", reply_markup=main_keyboard())
    elif text in ["CODM 1909 V1", "CODM 1909 V2", "ML FILE 1", "ML FILE 2", "ULP FILE"]:
        # --- FIX: CHECK KUNG PREMIUM BA TALAGA YUNG USER ---
        if user_id in premium_users or user_id == OWNER_ID:
            bot.send_message(message.chat.id, f"✅ Here is your file: {text}\n[Ilagay mo dito yung file link mo]")
        else:
            bot.send_message(message.chat.id, "🔒 File is locked. Redeem a key first.", reply_markup=main_keyboard())

# --- PAMPAGISING PARA HINDI MATULOG ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Alive!"
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()
bot.infinity_polling()
