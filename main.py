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

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"keys": {}, "users": {}, "stock_files": {"ML": [], "CODM": []}}
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            # FIX OLD DATA - kung string lang yung dati, gawing dict
            for g in ["ML", "CODM"]:
                new_list = []
                for x in d.get("stock_files", {}).get(g, []):
                    if isinstance(x, str):
                        new_list.append({"name": x, "file_id": None})
                    else:
                        new_list.append(x)
                d["stock_files"][g] = new_list
            return d
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

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ BACK", callback_data="back")]])

def redeem_only_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🎁 REDEEM KEY", callback_data="redeem")]])

# ============ START - BAGO: PAG BUYER AT WALANG KEY, REDEEM LANG ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _uid = None
    if update.message:
        _uid = update.message.from_user.id
    elif update.callback_query:
        _uid = update.callback_query.from_user.id

    # OWNER - full menu
    if _uid is not None and is_owner(_uid):
        text = "👋 **WELCOME TO YAGAMI BOT**\n\nChoose:\n• Generate Key\n• Redeem Key\n• ML / CODM TXT\n• Upload Files\n\nBot is Online ✅"
        _menu = main_menu(_uid)
    # BUYER NA WALANG KEY PA - REDEEM LANG
    elif _uid is not None and not is_authorized(_uid):
        text = "👋 **HI, WELCOME TO YAGAMI BOT**\n\nEnter your key here to redeem.\n\nPress REDEEM KEY below 👇"
        _menu = redeem_only_menu()
    # BUYER NA MAY KEY NA - user menu
    else:
        text = "👋 **WELCOME TO YAGAMI BOT**\n\nChoose:\n• Redeem Key\n• ML / CODM TXT\n• My Status\n\nBot is Online ✅"
        _menu = user_menu()

    if update.message:
        await update.message.reply_text(text, reply_markup=_menu, parse_mode="Markdown")
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=_menu, parse_mode="Markdown")
        except:
            await update.callback_query.message.reply_text(text, reply_markup=_menu, parse_mode="Markdown")

# ============ BUTTONS ============
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
        await query.edit_message_text(f"👤 **MY STATUS**\n\nExpire: {exp}\nAuthorized: {'YES ✅' if is_authorized(user_id) else 'NO ❌'}", reply_markup=back_menu(), parse_mode="Markdown")
        return
    if data == "stats":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Only Yagami Owner can view stats.", reply_markup=back_menu())
            return
        total_keys = len(keys_db)
        total_users = len(users_db)
        ml_count = len(stock_files.get("ML", []))
        codm_count = len(stock_files.get("CODM", []))
        await query.edit_message_text(f"📊 **STATS**\n\nTotal Keys: {total_keys}\nTotal Users: {total_users}\nML Files: {ml_count}\nCODM Files: {codm_count}", reply_markup=back_menu(), parse_mode="Markdown")
        return

    # === BAGO: ML / CODM LIST - CLICKABLE NA ===
    if data in ["ml_txt", "codm_txt"]:
        if not is_authorized(user_id):
            await query.edit_message_text("👋 **HI, WELCOME TO YAGAMI BOT**\n\nEnter your key here to redeem.", reply_markup=redeem_only_menu(), parse_mode="Markdown")
            return
        game = "ML" if data == "ml_txt" else "CODM"
        files = stock_files.get(game, [])
        if not files:
            await query.edit_message_text(f"📄 **{game} TXT**\n\nNo file uploaded yet.", reply_markup=back_menu(), parse_mode="Markdown")
            return
        # Gumawa ng button per file
        kb = []
        for idx, f in enumerate(files):
            name = f.get("name", "File") if isinstance(f, dict) else str(f)
            kb.append([InlineKeyboardButton(f"📄 {name}", callback_data=f"dl_{game}_{idx}")])
        kb.append([InlineKeyboardButton("⬅️ BACK", callback_data="back")])
        await query.edit_message_text(f"📄 **CHOOSE {game} FILE:**\n\nPindutin mo yung gusto mo i-download 👇", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    # === BAGO: DOWNLOAD FILE ===
    if data.startswith("dl_"):
        if not is_authorized(user_id):
            await query.edit_message_text("❌ You are not authorized. Redeem a key first.", reply_markup=back_menu())
            return
        try:
            _, game, idx = data.split("_")
            idx = int(idx)
            f = stock_files.get(game, [])[idx]
            file_id = f.get("file_id") if isinstance(f, dict) else None
            name = f.get("name", "File") if isinstance(f, dict) else str(f)
            if not file_id:
                await query.edit_message_text(f"❌ Old file ito, i-upload ulit ni Owner: {name}\n\nPa-upload ulit kay Owner.", reply_markup=back_menu())
                return
            await query.message.reply_document(document=file_id, filename=name, caption=f"📄 Here is your file: {name}")
            await query.answer("Sending file...")
        except Exception as e:
            await query.edit_message_text(f"❌ Error sending file: {e}", reply_markup=back_menu())
        return

    if data in ["upload_ml", "upload_codm"]:
        if not is_owner(user_id):
            await query.edit_message_text("❌ Only Yagami Owner can upload files.", reply_markup=back_menu())
            return
        game = "ML" if data == "upload_ml" else "CODM"
        waiting_upload[user_id] = game
        kb = [[InlineKeyboardButton("✅ DONE UPLOAD", callback_data="done_upload")], [InlineKeyboardButton("⬅️ BACK", callback_data="back")]]
        await query.edit_message_text(f"📤 **UPLOAD {game}**\n\nSend mo na yung 6 files mo, sunod-sunod lang.\nPag tapos ka na, pindutin mo DONE UPLOAD.", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
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
            await msg.reply_text(f"✅ **REDEEM SUCCESS!**\n\nYou are VIP until: {expire}\n\nNgayon pwede ka na pumili ng ML / CODM TXT 👇", reply_markup=_menu_to_return, parse_mode="Markdown")
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
            fid = msg.document.file_id
            game = waiting_upload[user_id]
            if game not in stock_files:
                stock_files[game] = []
            stock_files[game].append({"name": fname, "file_id": fid})
            save_data()
            count = len(stock_files[game])
            kb = [[InlineKeyboardButton("✅ DONE UPLOAD", callback_data="done_upload")]]
            await msg.reply_text(f"✅ Uploaded ({count}) to {game}: {fname}\n\nSend pa ulit ng next file, or pindutin DONE pag tapos na.", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await msg.reply_text("❌ Please send a file.", reply_markup=back_menu())
        # HINDI NA NATIN BUBURAHIN yung waiting_upload para tuloy-tuloy yung 6 files
        return
    await msg.reply_text("Use the menu below 👇", reply_markup=_menu_to_return)

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
