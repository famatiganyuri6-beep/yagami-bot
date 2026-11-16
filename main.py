import os
import random
import string
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# Storage files
KEYS_FILE = "keys.json"
AUTH_FILE = "authorized.json"

os.makedirs("codm", exist_ok=True)
os.makedirs("ml", exist_ok=True)

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

valid_keys = set(load_json(KEYS_FILE))
authorized = set(load_json(AUTH_FILE))
upload_mode = {}

def save_all():
    save_json(KEYS_FILE, list(valid_keys))
    save_json(AUTH_FILE, list(authorized))

def generate_key():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"YAGAMI-{code}"

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")],
        [InlineKeyboardButton("🔥 ML TXT", callback_data="ml")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")],
        [InlineKeyboardButton("🔥 ML TXT", callback_data="ml")],
        [InlineKeyboardButton("📤 Upload CODM", callback_data="upload_codm")],
        [InlineKeyboardButton("📤 Upload ML", callback_data="upload_ml")],
        [InlineKeyboardButton("🔑 Generate Key", callback_data="genkey")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

async def set_menu(app):
    commands = [
        BotCommand("start", "Start - Welcome to YAGAMI BOT"),
        BotCommand("codm", "CODM TXT List"),
        BotCommand("ml", "ML TXT List"),
        BotCommand("newkey", "Generate Key - Admin Only"),
        BotCommand("help", "Help"),
    ]
    await app.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authorized and user_id != ADMIN_ID:
        await update.message.reply_text(
            "🔒 Welcome to YAGAMI BOT\n\n"
            "This bot is LOCKED.\n"
            "Please enter your Entrance Key:"
        )
        return
    if user_id == ADMIN_ID:
        authorized.add(user_id)
        save_all()
        await update.message.reply_text(
            "👑 Welcome to YAGAMI BOT, Admin!\n\n"
            "You are the owner. Choose an option:",
            reply_markup=admin_menu()
        )
    else:
        await update.message.reply_text(
            "👋 Welcome to YAGAMI BOT!\n\n"
            "Choose an option:",
            reply_markup=main_menu()
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ HELP - YAGAMI BOT\n\n"
        "1. Type /start\n"
        "2. Enter your Entrance Key\n"
        "3. Press CODM TXT or ML TXT to view files\n\n"
        "Admin only:\n"
        "/newkey - Generate a new Entrance Key\n"
        "Upload via Upload buttons."
    )

async def newkey_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Only Admin can generate keys.")
        return
    key = generate_key()
    valid_keys.add(key)
    save_all()
    await update.message.reply_text(
        f"🔑 New Key Generated:\n\n`{key}`\n\n"
        "Send this key to your buyer. One key = One user only.",
        parse_mode="Markdown"
    )

async def codm_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authorized and user_id != ADMIN_ID:
        await update.message.reply_text("🔒 Locked. Type /start and enter your key.")
        return
    await send_file_list(update.message, "codm")

async def ml_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authorized and user_id != ADMIN_ID:
        await update.message.reply_text("🔒 Locked. Type /start and enter your key.")
        return
    await send_file_list(update.message, "ml")

async def send_file_list(message, category):
    files = [f for f in os.listdir(category) if f.endswith(".txt")]
    if not files:
        await message.reply_text(f"📂 No {category.upper()} TXT files yet.")
        return
    keyboard = [[InlineKeyboardButton(f, callback_data=f"get_{category}_{f}")] for f in files]
    await message.reply_text(
        f"📂 {category.upper()} TXT List:\n\nPress a file to download:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in authorized and user_id != ADMIN_ID:
        await query.message.reply_text("🔒 Locked. Type /start and enter your key.")
        return

    if data == "codm":
        await send_file_list(query.message, "codm")
    elif data == "ml":
        await send_file_list(query.message, "ml")
    elif data == "help":
        await query.message.reply_text(
            "❓ HELP - YAGAMI BOT\n\n"
            "Press CODM TXT or ML TXT to view files.\n"
            "Press a file name to download it."
        )
    elif data == "genkey":
        if user_id != ADMIN_ID:
            await query.message.reply_text("❌ Only Admin can generate keys.")
            return
        key = generate_key()
        valid_keys.add(key)
        save_all()
        await query.message.reply_text(f"🔑 New Key:\n\n`{key}`", parse_mode="Markdown")
    elif data == "upload_codm":
        if user_id != ADMIN_ID:
            return
        upload_mode[user_id] = "codm"
        await query.message.reply_text("📤 Upload Mode: CODM\n\nSend your .txt file now.")
    elif data == "upload_ml":
        if user_id != ADMIN_ID:
            return
        upload_mode[user_id] = "ml"
        await query.message.reply_text("📤 Upload Mode: ML\n\nSend your .txt file now.")
    elif data.startswith("get_"):
        parts = data.split("_", 2)
        category = parts[1]
        filename = parts[2]
        path = os.path.join(category, filename)
        if os.path.exists(path):
            await query.message.reply_document(document=open(path, "rb"), filename=filename)
        else:
            await query.message.reply_text("❌ File not found.")

async def check_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if user_id in authorized or user_id == ADMIN_ID:
        return
    if text in valid_keys:
        valid_keys.remove(text)
        authorized.add(user_id)
        save_all()
        await update.message.reply_text(
            "✅ Key Accepted! Welcome to YAGAMI BOT!\n\nChoose an option:",
            reply_markup=main_menu()
        )
    else:
        await update.message.reply_text("❌ Invalid Key. Please enter a valid Entrance Key:")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Only Admin can upload files.")
        return
    if user_id not in upload_mode:
        await update.message.reply_text("Press Upload CODM or Upload ML first.")
        return
    doc = update.message.document
    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("❌ Only .txt files allowed.")
        return
    category = upload_mode[user_id]
    file = await doc.get_file()
    path = os.path.join(category, doc.file_name)
    await file.download_to_drive(path)
    await update.message.reply_text(f"✅ Saved! {doc.file_name} in {category.upper()}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.post_init = set_menu
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("newkey", newkey_cmd))
    app.add_handler(CommandHandler("codm", codm_cmd))
    app.add_handler(CommandHandler("ml", ml_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_key))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
