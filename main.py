import os
import json
import random
import string
import asyncio
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 123456789
OWNER_USERNAME = "@YouknowLight"
DATA_FILE = "data.json"
try:
    OWNER_ID = int(os.environ.get("ADMIN_ID", str(OWNER_ID)))
except:
    pass
def is_owner(user_id):
    try:
        return int(user_id) == int(OWNER_ID)
    except:
        return False
GAMES = ["ML", "CODM", "COC", "GMAIL", "GLOBAL"]
GAME_NAME = {"ML": "ML", "CODM": "CODM", "COC": "COC", "GMAIL": "GMAIL", "GLOBAL": "GLOBAL-CODM"}
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"keys": {}, "users": {}, "stock_files": {g: [] for g in GAMES}}
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            if "stock_files" not in d:
                d["stock_files"] = {}
            for g in GAMES:
                if g not in d["stock_files"]:
                    d["stock_files"][g] = []
                new_list = []
                for x in d["stock_files"].get(g, []):
                    if isinstance(x, str):
                        new_list.append({"name": x, "file_id": None})
                    else:
                        new_list.append(x)
                d["stock_files"][g] = new_list
            return d
    except:
        return {"keys": {}, "users": {}, "stock_files": {g: [] for g in GAMES}}
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
def main_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("🔑 GENERATE 10 DAYS", callback_data="gen_10")],
        [InlineKeyboardButton("🔑 GENERATE 20 DAYS", callback_data="gen_20")],
        [InlineKeyboardButton("🔑 GENERATE 50 DAYS", callback_data="gen_50")],
        [InlineKeyboardButton("👑 GENERATE LIFETIME", callback_data="gen_lifetime")],
        [InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")],
        [InlineKeyboardButton("🎮 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("🔫 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("🏰 COC TXT", callback_data="coc_txt"), InlineKeyboardButton("📧 GMAIL TXT", callback_data="gmail_txt")],
        [InlineKeyboardButton("🌍 GLOBAL-CODM TXT", callback_data="global_txt")],
        [InlineKeyboardButton("📤 UPLOAD ML", callback_data="upload_ml"), InlineKeyboardButton("📤 UPLOAD CODM", callback_data="upload_codm")],
        [InlineKeyboardButton("📤 UPLOAD COC", callback_data="upload_coc"), InlineKeyboardButton("📤 UPLOAD GMAIL", callback_data="upload_gmail")],
        [InlineKeyboardButton("📤 UPLOAD GLOBAL-CODM", callback_data="upload_global")],
        [InlineKeyboardButton("📊 STATS", callback_data="stats"), InlineKeyboardButton("👤 MY STATUS", callback_data="status")],
    ]
    return InlineKeyboardMarkup(keyboard)
def user_menu():
    keyboard = [
        [InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")],
        [InlineKeyboardButton("🎮 ML TXT", callback_data="ml_txt"), InlineKeyboardButton("🔫 CODM TXT", callback_data="codm_txt")],
        [InlineKeyboardButton("🏰 COC TXT", callback_data="coc_txt"), InlineKeyboardButton("📧 GMAIL TXT", callback_data="gmail_txt")],
        [InlineKeyboardButton("🌍 GLOBAL-CODM TXT", callback_data="global_txt")],
        [InlineKeyboardButton("👤 MY STATUS", callback_data="status")],
    ]
    return InlineKeyboardMarkup(keyboard)
def get_menu(user_id=None):
    if user_id is not None and is_owner(user_id):
        return main_menu(user_id)
    return user_menu()
def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ BACK", callback_data="back")]])
def redeem_only_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")]])
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _uid = None
    if update.message:
        _uid = update.message.from_user.id
    elif update.callback_query:
        _uid = update.callback_query.from_user.id
    if _uid is not None and is_owner(_uid):
        text = "⚡ YAGAMI BOT ⚡\n👑 WELCOME TO YAGAMI BOT 👑\nOwner: @YouknowLight\nChoose:\n- 🔑 Generate Key\n- 🎁 Redeem Key\n- 📁 ML / CODM / COC / GMAIL / GLOBAL-CODM TXT\n- 📤 Upload Files\n🟢 Bot is Online"
        _menu = main_menu(_uid)
    elif _uid is not None and not is_authorized(_uid):
        text = "👋 HI, WELCOME TO YAGAMI BOT\n🎁 Enter your key here to redeem.\n👇 Press REDEEM KEY below"
        _menu = redeem_only_menu()
    else:
        text = "⚡ YAGAMI BOT ⚡\n👋 WELCOME TO YAGAMI BOT\nChoose:\n- 🎁 Redeem Key\n- 📁 ML / CODM / COC / GMAIL / GLOBAL-CODM TXT\n- 👤 My Status\n🟢 Bot is Online"
        _menu = user_menu()
    if update.message:
        await update.message.reply_text(text, reply_markup=_menu)
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=_menu)
        except:
            await update.callback_query.message.reply_text(text, reply_markup=_menu)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    if data == "back":
        await start(update, context)
        return
    if data == "done_upload":
        if user_id in waiting_upload:
            del waiting_upload[user_id]
        await start(update, context)
        return
    if data == "status":
        u = users_db.get(str(user_id), {})
        exp = u.get("expire", "You have no VIP yet")
        auth = "YES" if is_authorized(user_id) else "NO"
        text = "👤 MY STATUS\n\nExpire: " + str(exp) + "\nAuthorized: " + auth
        await query.edit_message_text(text, reply_markup=back_menu())
        return
    if data == "stats":
        if not is_owner(user_id):
            await query.edit_message_text("Only @YouknowLight can view stats.", reply_markup=back_menu())
            return
        txt = "📊 STATS\n\n"
        txt += "Total Keys: " + str(len(keys_db)) + "\n"
        txt += "Total Users: " + str(len(users_db)) + "\n"
        for g in GAMES:
            txt += GAME_NAME[g] + " Files: " + str(len(stock_files.get(g, []))) + "\n"
        await query.edit_message_text(txt, reply_markup=back_menu())
        return
    txt_map = {"ml_txt": "ML", "codm_txt": "CODM", "coc_txt": "COC", "gmail_txt": "GMAIL", "global_txt": "GLOBAL"}
    if data in txt_map:
        if not is_authorized(user_id):
            await query.edit_message_text("HI, WELCOME TO YAGAMI BOT\n\nEnter your key here to redeem.", reply_markup=redeem_only_menu())
            return
        game = txt_map[data]
        files = stock_files.get(game, [])
        if not files:
            await query.edit_message_text(GAME_NAME[game] + " TXT\n\nNo file uploaded yet.", reply_markup=back_menu())
            return
        kb = []
        for idx, f in enumerate(files):
            name = f.get("name", "File") if isinstance(f, dict) else str(f)
            kb.append([InlineKeyboardButton(name, callback_data="dl_" + game + "_" + str(idx))])
        kb.append([InlineKeyboardButton("⬅️ BACK", callback_data="back")])
        await query.edit_message_text("CHOOSE " + GAME_NAME[game] + " FILE:\n\nClick the file you want to download", reply_markup=InlineKeyboardMarkup(kb))
        return
    if data.startswith("dl_"):
        if not is_authorized(user_id):
            await query.edit_message_text("You are not authorized. Redeem a key first.", reply_markup=back_menu())
            return
        try:
            parts = data.split("_")
            game = parts[1]
            idx = int(parts[2])
            f = stock_files.get(game, [])[idx]
            file_id = f.get("file_id") if isinstance(f, dict) else None
            name = f.get("name", "File") if isinstance(f, dict) else str(f)
            if not file_id:
                await query.edit_message_text("This is an old file, please ask Owner to re-upload: " + name, reply_markup=back_menu())
                return
            await query.message.reply_document(document=file_id, filename=name, caption="Here is your file: " + name)
            await query.answer("Sending file...")
        except Exception as e:
            await query.edit_message_text("Error sending file: " + str(e), reply_markup=back_menu())
        return
    upload_map = {"upload_ml": "ML", "upload_codm": "CODM", "upload_coc": "COC", "upload_gmail": "GMAIL", "upload_global": "GLOBAL"}
    if data in upload_map:
        if not is_owner(user_id):
            await query.edit_message_text("Only @YouknowLight can upload files.", reply_markup=back_menu())
            return
        game = upload_map[data]
        waiting_upload[user_id] = game
        kb = [[InlineKeyboardButton("✅ DONE UPLOAD", callback_data="done_upload")], [InlineKeyboardButton("⬅️ BACK", callback_data="back")]]
        await query.edit_message_text("📤 UPLOAD " + GAME_NAME[game] + "\n\nSend your files one by one.\nWhen you are done, press DONE UPLOAD.", reply_markup=InlineKeyboardMarkup(kb))
        return
    if data == "redeem":
        waiting_redeem.add(user_id)
        await query.edit_message_text("🎁 REDEEM KEY\n\nSend your KEY.\nExample: YAGAMI-XXXX...", reply_markup=back_menu())
        return
    if data.startswith("gen_"):
        if not is_owner(user_id):
            await query.edit_message_text("Only owner @YouknowLight can generate the key.", reply_markup=back_menu())
            return
        days_map = {"gen_10": 10, "gen_20": 20, "gen_50": 50, "gen_lifetime": 9999}
        days = days_map.get(data, 10)
        key = gen_key()
        keys_db[key] = {"days": days, "created": str(datetime.now()), "used": False}
        save_data()
        label = "LIFETIME" if days == 9999 else str(days) + " DAYS"
        await query.edit_message_text("✅ GENERATED " + label + "\n\nKey:\n" + key + "\n\nCopy and redeem it.", reply_markup=back_menu())
        return
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message
    _menu_to_return = get_menu(user_id)
    txt = (msg.text or "").strip().lower()
    if txt in ["genkey", "/genkey", "gen", "generate", "generate key", "/generate", "gen key", "/gen"]:
        if not is_owner(user_id):
            await msg.reply_text("Only owner @YouknowLight can generate the key.", reply_markup=back_menu())
            return
        else:
            await msg.reply_text("You are the Owner, please use the GENERATE button in the menu", reply_markup=_menu_to_return)
        return
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
            await msg.reply_text("✅ REDEEM SUCCESS!\n\nYou are VIP until: " + expire + "\n\nNow you can choose ML / CODM / COC / GMAIL / GLOBAL-CODM TXT", reply_markup=_menu_to_return)
        else:
            await msg.reply_text("Invalid or already used KEY.", reply_markup=back_menu())
        waiting_redeem.discard(user_id)
        return
    if user_id in waiting_upload:
        if not is_owner(user_id):
            await msg.reply_text("Only @YouknowLight can upload files.", reply_markup=back_menu())
            del waiting_upload[user_id]
            return
        if msg.document:
            fname = msg.document.file_name
            fid = msg.document.file_id
            game = waiting_upload[user_id]
            if game not in stock_files:
                stock_files[game] = []
            stock_files[game].append({"name": fname, "file_id": fid})
            save_data()
            count = len(stock_files[game])
            kb = [[InlineKeyboardButton("✅ DONE UPLOAD", callback_data="done_upload")]]
            await msg.reply_text("✅ Uploaded (" + str(count) + ") to " + GAME_NAME[game] + ": " + fname + "\n\nSend another file, or press DONE when finished.", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await msg.reply_text("Please send a file.", reply_markup=back_menu())
        return
    await msg.reply_text("Use the menu below", reply_markup=_menu_to_return)
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
web_app = Flask('')
@web_app.route('/')
def home():
    return "YAGAMI Bot is Alive!"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)
def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except Exception:
        pass
    keep_alive()
    main()
