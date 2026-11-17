import os
import json
import random
import string
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ============ CONFIG ============
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 123456789
DATA_FILE = "data.json"

# ============ ADDED ONLY - OWNER LOCK ============
try:
    OWNER_ID = int(os.environ.get("ADMIN_ID", str(OWNER_ID)))
except:
    pass

def is_owner(user_id):
    try:
        return int(user_id) == int(OWNER_ID)
    except:
        return False
# ============ END ADDED ============

# ============ DATA ============
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"keys": {}, "users": {}, "stock_files": {"ML": [], "CODM": []}}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"keys": {}, "users": {}, "stock_files": {"ML": [], "CODM": []}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

DATA = load_data()
keys_db = DATA["keys"]
users_db = DATA["users"]
stock_files = DATA["stock_files"]
waiting_redeem = set()
waiting_upload = {}

def gen_key():
    return "YAGAMI-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

def is_authorized(user_id):
    if user_id == OWNER_ID:
        return True
    u = users_db.get(str(user_id))
    if not u:
        return False
    exp = u.get("expire", "")
    if exp == "LIFETIME":
        return True
    try:
        return datetime.fromisoformat(exp) > datetime.now()
    except:
        return False

# ============ MENUS ============
def main_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("🎮 GENERATE 10 DAYS", callback_data="gen_10")],
        [InlineKeyboardButton("🎮 GENERATE 20 DAYS", callback_data="gen_20")],
        [InlineKeyboardButton("🎮 GENERATE 50 DAYS", callback_data="gen_50")],
        [InlineKeyboardButton("👑 GENERATE LIFETIME", callback_data="gen_lifetime")],
        [InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")],
        [InlineKeyboardButton("📄 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("📄 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("📤 UPLOAD ML", callback_data="upload_ml"), InlineKeyboardButton("📤 UPLOAD CODM", callback_data="upload_codm")],
        [InlineKeyboardButton("📊 STATS", callback_data="stats"), InlineKeyboardButton("👤 MY STATUS", callback_data="status")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ============ ADDED ONLY - USER MENU ============
def user_menu():
    keyboard = [
        [InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")],
        [InlineKeyboardButton("📄 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("📄 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("👤 MY STATUS", callback_data="status")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_menu(user_id=None):
    if user_id is not None and is_owner(user_id):
        return main_menu(user_id)
    return user_menu()
# ============ END ADDED ============

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ BACK", callback_data="back")]])

# ============ START - ITO LANG YUNG PINALITAN KO ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _uid = None
    if update.message:
        _uid = update.message.from_user.id
    elif update.callback_query:
        _uid = update.callback_query.from_user.id
    _menu = get_menu(_uid)
    text = "👋 **WELCOME TO YAGAMI BOT**\n\nChoose:\n• Generate Key\n• Redeem Key\n• ML / CODM TXT\n• Upload Files\n\nBot is Online ✅"
    if _uid is not None and not is_owner(_uid):
        text = "👋 **WELCOME TO YAGAMI BOT**\n\nChoose:\n• Redeem Key\n• ML / CODM TXT\n• My Status\n\nBot is Online ✅"
    if update.message:
        await update.message.reply_text(text, reply_markup=_menu, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=_menu, parse_mode="Markdown")
# ============ END START ============

# ============ BUTTONS ============
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    if data == "back":
        await start(update, context)
        return
    if data == "status":
        u = users_db.get(str(user_id), {})
        exp = u.get("expire", "You have no VIP yet")
        await query.edit_message_text(f"👤 **MY STATUS**\n\nExpire: {exp}\nAuthorized: {'YES ✅' if is_authorized(user_id) else 'NO ❌'}", reply_markup=back_menu(), parse_mode="Markdown")
        return
    if data == "stats":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Only Yagami Owner can view stats.", reply_markup=back_menu())
            return
        if not is_authorized(user_id):
            await query.edit_message_text("❌ You are not authorized. Redeem a key first.", reply_markup=back_menu())
            return
        total_keys = len(keys_db)
        total_users = len(users_db)
        ml_count = len(stock_files.get("ML", []))
        codm_count = len(stock_files.get("CODM", []))
        await query.edit_message_text(f"📊 **STATS**\n\nTotal Keys: {total_keys}\nTotal Users: {total_users}\nML Files: {ml_count}\nCODM Files: {codm_count}", reply_markup=back_menu(), parse_mode="Markdown")
        return
    if data in ["ml_txt", "codm_txt"]:
        if not is_authorized(user_id):
            await query.edit_message_text("❌ You are not authorized. Redeem a key first to view TXT.", reply_markup=back_menu())
            return
        game = "ML" if data == "ml_txt" else "CODM"
        files = stock_files.get(game, [])
        if not files:
            await query.edit_message_text(f"📄 **{game} TXT**\n\nNo file uploaded yet.", reply_markup=back_menu(), parse_mode="Markdown")
            return
        txt = f"📄 **{game} TXT FILES**\n\n"
        for f in files:
            txt += f"• {f}\n"
        await query.edit_message_text(txt, reply_markup=back_menu(), parse_mode="Markdown")
        return
    if data in ["upload_ml", "upload_codm"]:
        if not is_owner(user_id):
            await query.edit_message_text("❌ Only Yagami Owner can upload files.", reply_markup=back_menu())
            return
        if user_id != OWNER_ID:
            await query.edit_message_text("❌ Only Yagami Owner can upload files.", reply_markup=back_menu())
            return
        game = "ML" if data == "upload_ml" else "CODM"
        waiting_upload[user_id] = game
        await query.edit_message_text(f"📤 **UPLOAD {game}**\n\nSend your file now.", reply_markup=back_menu(), parse_mode="Markdown")
        return
    if data == "redeem":
        waiting_redeem.add(user_id)
        await query.edit_message_text("🎁 **REDEEM KEY**\n\nSend your KEY.\nExample: `YAGAMI-XXXX...`", reply_markup=back_menu(), parse_mode="Markdown")
        return
    if data.startswith("gen_"):
        if not is_owner(user_id):
            await query.edit_message_text("❌ Only Yagami Owner can generate key.", reply_markup=back_menu())
            return
        days_map = {"gen_10": 10, "gen_20": 20, "gen_50": 50, "gen_lifetime": 9999}
        days = days_map.get(data, 10)
        key = gen_key()
        keys_db[key] = {"days": days, "created": str(datetime.now()), "used": False}
        save_data()
        label = "LIFETIME" if days == 9999 else f"{days} DAYS"
        await query.edit_message_text(f"✅ **GENERATED {label}**\n\nKey:\n`{key}`\n\nCopy and redeem it.", reply_markup=back_menu(), parse_mode="Markdown")
        return

# ============ MESSAGES ============
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message
    _menu_to_return = get_menu(user_id)
    if user_id in waiting_redeem:
        key = (msg.text or "").strip().upper()
        if key in keys_db and not keys_db[key]["used"]:
            days = keys_db[key]["days"]
            keys_db[key]["used"] = True
            if days == 9999:
                expire = "LIFETIME"
            else:
                expire = str(datetime.now() + timedelta(days=days))
            users_db[str(user_id)] = {"expire": expire, "key": key}
            save_data()
            await msg.reply_text(f"✅ **REDEEM SUCCESS!**\n\nYou are VIP until: {expire}", reply_markup=_menu_to_return, parse_mode="Markdown")
        else:
            await msg.reply_text("❌ Invalid or already used KEY.", reply_markup=back_menu())
        waiting_redeem.discard(user_id)
        return
    if user_id in waiting_upload:
        if not is_owner(user_id):
            await msg.reply_text("❌ Only Yagami Owner can upload files.", reply_markup=back_menu())
            del waiting_upload[user_id]
            return
        if msg.document:
            fname = msg.document.file_name
            game = waiting_upload[user_id]
            if game not in stock_files:
                stock_files[game] = []
            stock_files[game].append(fname)
            save_data()
            await msg.reply_text(f"✅ Uploaded to {game}: {fname}", reply_markup=_menu_to_return)
        else:
            await msg.reply_text("❌ Please send a file.", reply_markup=back_menu())
        del waiting_upload[user_id]
        return
    await msg.reply_text("Use the menu below 👇", reply_markup=_menu_to_return)

# ============ MAIN BOT ============
def main():
    if not BOT_TOKEN:
        print("ERROR: No BOT_TOKEN in Render!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, message_handler))
    print("YAGAMI Bot is running...")
    app.run_polling()

# ============ KEEP ALIVE FOR RENDER ============
web_app = Flask('')
@web_app.route('/')
def home():
    return "YAGAMI Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

if __name__ == "__main__":
    keep_alive()
    main()
