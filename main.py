import telebot
from telebot import types

# PALITAN MO TO NG TOKEN MO
TOKEN = "9073043795:AAFD2xWxqzgi0v2FzJ4F78_tThRfljv8F3Y"
bot = telebot.TeleBot(TOKEN)

# ========== START ==========
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("YAGAMIHAXX TXT")
    bot.send_message(message.chat.id, "Welcome sa YAGAMIHAXX TXT!\n\nPindutin mo yung button sa baba:", reply_markup=markup)

# ========== YAGAMIHAXX TXT - ISANG PINDOT LANG ==========
@bot.message_handler(func=lambda m: m.text == "YAGAMIHAXX TXT")
def yagamihaxx_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("CODM 1909 V1", "CODM 1909 V2")
    markup.add("CODM 1908 V1", "CODM 1908 MIX V1")
    markup.add("CODM 1908 MIX", "CODM CLEAN")
    markup.add("CODM 20261116")
    markup.add("⬅️ BACK")
    bot.send_message(message.chat.id, "Pili ka ng file na gusto mo:", reply_markup=markup)

# ========== BACK ==========
@bot.message_handler(func=lambda m: m.text == "⬅️ BACK")
def back(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("YAGAMIHAXX TXT")
    bot.send_message(message.chat.id, "Balik sa main menu:", reply_markup=markup)

# ========== 7 FILES - PAG PININDOT, YUN LANG MA-SEND ==========
# PALITAN MO YUNG USERNAME/REPO NG SAYO!

@bot.message_handler(func=lambda m: m.text == "CODM 1909 V1")
def send_1909_v1(message):
    bot.send_document(message.chat.id, "https://raw.githubusercontent.com/USERNAME/REPO/main/files/Codm_0725_1909.txt", caption="YAGAMIHAXX TXT - CODM 1909 V1")

@bot.message_handler(func=lambda m: m.text == "CODM 1909 V2")
def send_1909_v2(message):
    bot.send_document(message.chat.id, "https://raw.githubusercontent.com/USERNAME/REPO/main/files/Codm_0725_1909_1.txt", caption="YAGAMIHAXX TXT - CODM 1909 V2")

@bot.message_handler(func=lambda m: m.text == "CODM 1908 V1")
def send_1908_v1(message):
    bot.send_document(message.chat.id, "https://raw.githubusercontent.com/USERNAME/REPO/main/files/Codm_0725_1908_1.txt", caption="YAGAMIHAXX TXT - CODM 1908 V1")

@bot.message_handler(func=lambda m: m.text == "CODM 1908 MIX V1")
def send_1908_mix_v1(message):
    bot.send_document(message.chat.id, "https://raw.githubusercontent.com/USERNAME/REPO/main/files/Mix_Codm_0725_1908_1.txt", caption="YAGAMIHAXX TXT - CODM 1908 MIX V1")

@bot.message_handler(func=lambda m: m.text == "CODM 1908 MIX")
def send_1908_mix(message):
    bot.send_document(message.chat.id, "https://raw.githubusercontent.com/USERNAME/REPO/main/files/Mix_Codm_0725_1908.txt", caption="YAGAMIHAXX TXT - CODM 1908 MIX")

@bot.message_handler(func=lambda m: m.text == "CODM CLEAN")
def send_clean(message):
    bot.send_document(message.chat.id, "https://raw.githubusercontent.com/USERNAME/REPO/main/files/clean_codm_1.txt", caption="YAGAMIHAXX TXT - CODM CLEAN")

@bot.message_handler(func=lambda m: m.text == "CODM 20261116")
def send_2026(message):
    bot.send_document(message.chat.id, "https://raw.githubusercontent.com/USERNAME/REPO/main/files/20261116_1.txt", caption="YAGAMIHAXX TXT - CODM 20261116")

# ========== RUN ==========
print("YAGAMIHAXX BOT RUNNING...")
bot.polling(none_stop=True)
