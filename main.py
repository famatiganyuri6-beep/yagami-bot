import telebot
import os
import random
import string
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 8089763801
ADMIN_IDS = set([8089763801])
MASTER_KEY = "YAGAMIOWNBOT+7914&"

bot = telebot.TeleBot(TOKEN)
keys_db = {}
used_keys = set()

CATEGORIES = {
    "CODM": [("CODM 1909 V1", "codm_1909_v1.py"), ("CODM 1909 V2", "codm_1909_v2.py"), ("CODM 1908", "codm_1908.py"), ("MIX CODM", "mix_codm.py")],
    "ML": [("ML FILE 1", "ml1.py"), ("ML FILE 2", "ml2.py")],
    "ULP": [("ULP FILE", "ulp.py")],
}

def generate_key():
    return "YAGAMI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔑 REDEEM KEY", callback_data="menu_redeem"))
    markup.add(types.InlineKeyboardButton("🎮 CODM", callback_data="menu_codm"))
    markup.add(types.InlineKeyboardButton("🎮 ML", callback_data="menu_ml"))
    markup.add(types.InlineKeyboardButton("🛠️ ULP", callback_data="menu_ulp"))
    markup.add(types.InlineKeyboardButton("📢 CHANNEL", callback_data="menu_channel"))
    markup.add(types.InlineKeyboardButton("ℹ️ ABOUT", callback_data="menu_about"))
    return markup

def show_files_inline(chat_id, category):
    files = CATEGORIES.get(category, [])
    markup = types.InlineKeyboardMarkup()
    for title, filename in files:
        markup.add(types.InlineKeyboardButton(title, callback_data=f"file_{category}_{filename}"))
    markup.add(types.InlineKeyboardButton("⬅️ BACK", callback_data="back_menu"))
    bot.send_message(chat_id, f"📂 {category} Files:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def menu_callback(call):
    if call.data == "menu_codm":
        show_files_inline(call.message.chat.id, "CODM")
    elif call.data == "menu_ml":
        show_files_inline(call.message.chat.id, "ML")
    elif call.data == "menu_ulp":
        show_files_inline(call.message.chat.id, "ULP")
    elif call.data == "menu_redeem":
        bot.send_message(call.message.chat.id, "Send: /redeem YAGAMI-XXXX")
    elif call.data == "menu_channel":
        bot.send_message(call.message.chat.id, "Channel: https://t.me/yagami")
    elif call.data == "menu_about":
        bot.send_message(call.message.chat.id, "Yagami Bot by Owner")
    elif call.data == "back_menu":
        bot.send_message(call.message.chat.id, "Choose:", reply_markup=main_menu())
    bot.answer_callback_query(call.id)

if bot:
    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id, "Yagami Bot is Online! What do you want?", reply_markup=main_menu())

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
                bot.reply_to(message, "✅ Key Accepted! Premium Unlocked.")
            else:
                bot.reply_to(message, "❌ Invalid or Already Used.")
        except:
            bot.reply_to(message, "Use: /redeem YAGAMI-XXXX")

print("Bot is running...")
bot.polling(none_stop=True)
