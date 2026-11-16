
import os
import asyncio
import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timezone

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==============================
# CONFIGURATION
# ==============================

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

DB_PATH = os.environ.get(
    "DATABASE_PATH",
    "/var/data/yagami.db"
)

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


# ==============================
# DATABASE
# ==============================

def db():
    return sqlite3.connect(DB_PATH)


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                key_hash TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game TEXT NOT NULL,
                label TEXT NOT NULL,
                added_at TEXT NOT NULL
            )
        """)


def now():
    return datetime.now(timezone.utc).isoformat()


def hash_key(key):
    return hashlib.sha256(key.encode()).hexdigest()


def is_authorized(user_id):
    if user_id == ADMIN_ID:
        return True

    with db() as conn:
        result = conn.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

    return result is not None


def generate_key():
    return "YAGAMI-" + secrets.token_hex(4).upper()


def save_key(key):
    with db() as conn:
        conn.execute(
            "INSERT INTO keys (key_hash, created_at) VALUES (?, ?)",
            (hash_key(key), now())
        )


def redeem_key(user_id, key):
    with db() as conn:
        result = conn.execute(
            "SELECT key_hash FROM keys WHERE key_hash = ?",
            (hash_key(key),)
        ).fetchone()

        if not result:
            return False

        conn.execute(
            "DELETE FROM keys WHERE key_hash = ?",
            (hash_key(key),)
        )

        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, created_at) VALUES (?, ?)",
            (user_id, now())
        )

    return True


# ==============================
# KEYBOARDS
# ==============================

def main_menu(is_admin=False):
    buttons = [
        [
            InlineKeyboardButton(
                "🎮 CODM TXT",
                callback_data="codm"
            ),
            InlineKeyboardButton(
                "🔥 ML TXT",
                callback_data="ml"
            )
        ],
        [
            InlineKeyboardButton(
                "❓ Help",
                callback_data="help"
            )
        ]
    ]

    if is_admin:
        buttons.append([
            InlineKeyboardButton(
                "👑 OWNER PANEL",
                callback_data="panel"
            )
        ])

    return InlineKeyboardMarkup(buttons)


def owner_menu():
    buttons = [
        [
            InlineKeyboardButton(
                "🔑 Generate Key",
                callback_data="genkey"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Manage Users",
                callback_data="users"
            ),
            InlineKeyboardButton(
                "📊 Statistics",
                callback_data="stats"
            )
        ],
        [
            InlineKeyboardButton(
                "📁 Catalog Info",
                callback_data="catalog_info"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Back to Menu",
                callback_data="home"
            )
        ]
    ]

    return InlineKeyboardMarkup(buttons)


# ==============================
# START COMMAND
# ==============================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        await update.effective_message.reply_text(
            "👑 Welcome to YAGAMI BOT, Owner!",
            reply_markup=main_menu(True)
        )

    elif is_authorized(user_id):
        await update.effective_message.reply_text(
            "👋 Welcome to YAGAMI BOT!",
            reply_markup=main_menu(False)
        )

    else:
        await update.effective_message.reply_text(
            "🔒 Welcome to YAGAMI BOT\n\n"
            "This bot is private.\n"
            "Please enter your Entrance Key:"
        )


# ==============================
# GENERATE KEY
# ==============================

async def newkey(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_user.id != ADMIN_ID:
        await update.effective_message.reply_text(
            "❌ Owner access only."
        )
        return

    key = generate_key()
    save_key(key)

    await update.effective_message.reply_text(
        f"🔑 NEW ENTRANCE KEY\n\n{key}\n\n"
        "This key can only be used once."
    )


# ==============================
# KEY VERIFICATION
# ==============================

async def check_key(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    text = update.effective_message.text.strip()

    if is_authorized(user_id):
        await update.effective_message.reply_text(
            "Use the buttons to navigate the bot."
        )
        return

    if redeem_key(user_id, text):
        await update.effective_message.reply_text(
            "✅ Key Accepted!\n"
            "Welcome to YAGAMI BOT!",
            reply_markup=main_menu(False)
        )
    else:
        await update.effective_message.reply_text(
            "❌ Invalid or already used key.\n"
            "Please try again."
        )


# ==============================
# CATALOG MANAGEMENT
# ==============================

async def add_catalog(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    game: str
):
    if update.effective_user.id != ADMIN_ID:
        await update.effective_message.reply_text(
            "❌ Owner access only."
        )
        return

    label = " ".join(context.args).strip()

    if not label:
        await update.effective_message.reply_text(
            f"Usage: /add{game.lower()} Account 001"
        )
        return

    if len(label) > 60 or any(
        word in label.lower()
        for word in ("password", "passwd", "login", "token", "email")
    ) or "@" in label:
        await update.effective_message.reply_text(
            "❌ Use a short, non-sensitive account label only."
        )
        return

    with db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO catalog (game, label, added_at)
            VALUES (?, ?, ?)
            """,
            (game, label, now())
        )
        item_id = cursor.lastrowid

    await update.effective_message.reply_text(
        f"✅ Catalog entry added!\n\n"
        f"Game: {game}\n"
        f"ID: {item_id}\n"
        f"Label: {label}"
    )


async def addcodm(update, context):
    await add_catalog(update, context, "CODM")


async def addml(update, context):
    await add_catalog(update, context, "ML")


async def delete_item(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_user.id != ADMIN_ID:
        await update.effective_message.reply_text(
            "❌ Owner access only."
        )
        return

    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text(
            "Usage: /delitem 1"
        )
        return

    item_id = int(context.args[0])

    with db() as conn:
        cursor = conn.execute(
            "DELETE FROM catalog WHERE id = ?",
            (item_id,)
        )

    if cursor.rowcount:
        await update.effective_message.reply_text(
            "✅ Catalog entry deleted."
        )
    else:
        await update.effective_message.reply_text(
            "❌ Catalog entry not found."
        )


async def show_catalog(
    message,
    game: str
):
    with db() as conn:
        rows = conn.execute(
            """
            SELECT id, label FROM catalog
            WHERE game = ?
            ORDER BY id DESC
            """,
            (game,)
        ).fetchall()

    if not rows:
        await message.reply_text(
            f"📁 {game} CATALOG\n\nNo account entries available."
        )
        return

    lines = [
        f"📁 {game} ACCOUNT CATALOG",
        ""
    ]

    for item_id, label in rows:
        lines.append(f"#{item_id} - {label}")

    lines.append("")
    lines.append("🔒 Login credentials are not displayed.")

    await message.reply_text("\n".join(lines))


# ==============================
# OWNER INFORMATION
# ==============================

async def show_users(message):
    with db() as conn:
        rows = conn.execute(
            "SELECT user_id FROM users ORDER BY created_at DESC LIMIT 30"
        ).fetchall()

        total = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

    lines = [
        "👥 AUTHORIZED USERS",
        f"Total Users: {total}",
        ""
    ]

    if rows:
        for row in rows:
            lines.append(f"• {row[0]}")
    else:
        lines.append("No authorized users yet.")

    await message.reply_text("\n".join(lines))


async def show_stats(message):
    with db() as conn:
        users = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        keys = conn.execute(
            "SELECT COUNT(*) FROM keys"
        ).fetchone()[0]

        codm = conn.execute(
            "SELECT COUNT(*) FROM catalog WHERE game = 'CODM'"
        ).fetchone()[0]

        ml = conn.execute(
            "SELECT COUNT(*) FROM catalog WHERE game = 'ML'"
        ).fetchone()[0]

    await message.reply_text(
        "📊 YAGAMI BOT STATISTICS\n\n"
        f"👥 Authorized Users: {users}\n"
        f"🔑 Unused Keys: {keys}\n"
        f"🎮 CODM Entries: {codm}\n"
        f"🔥 ML Entries: {ml}"
    )


# ==============================
# BUTTON HANDLER
# ==============================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if not is_authorized(user_id):
        await query.message.reply_text(
            "🔒 Access denied. Please enter your Entrance Key."
        )
        return

    if data == "codm":
        await show_catalog(query.message, "CODM")

    elif data == "ml":
        await show_catalog(query.message, "ML")

    elif data == "help":
        await query.message.reply_text(
            "❓ YAGAMI BOT HELP\n\n"
            "1. Generate an entrance key from the Owner Panel.\n"
            "2. Enter the key to gain access.\n"
            "3. Select CODM TXT or ML TXT.\n"
            "4. Browse the safe account catalog."
        )

    elif data == "panel":
        if user_id != ADMIN_ID:
            await query.message.reply_text(
                "❌ Owner access only."
            )
            return

        await query.message.reply_text(
            "👑 YAGAMI OWNER PANEL\n\n"
            "Select an option:",
            reply_markup=owner_menu()
        )

    elif data == "genkey":
        if user_id != ADMIN_ID:
            return

        key = generate_key()
        save_key(key)

        await query.message.reply_text(
            f"🔑 NEW ENTRANCE KEY\n\n{key}\n\n"
            "Single-use key generated successfully."
        )

    elif data == "users":
        if user_id == ADMIN_ID:
            await show_users(query.message)

    elif data == "stats":
        if user_id == ADMIN_ID:
            await show_stats(query.message)

    elif data == "catalog_info":
        if user_id == ADMIN_ID:
            await query.message.reply_text(
                "📁 CATALOG MANAGEMENT\n\n"
                "Add CODM entry:\n"
                "/addcodm Account 001\n\n"
                "Add ML entry:\n"
                "/addml Account 001\n\n"
                "Delete entry:\n"
                "/delitem 1\n\n"
                "Use labels only. Never enter passwords or login details."
            )

    elif data == "home":
        await query.message.reply_text(
            "🏠 Main Menu",
            reply_markup=main_menu(user_id == ADMIN_ID)
        )


# ==============================
# DOCUMENT SECURITY
# ==============================

async def reject_documents(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.effective_message.reply_text(
        "🔒 File uploads are disabled for security.\n\n"
        "Please use the safe account catalog instead."
    )


# ==============================
# HELP COMMAND
# ==============================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.effective_message.reply_text(
        "❓ YAGAMI BOT HELP\n\n"
        "/start - Open main menu\n"
        "/help - Show help\n"
        "/newkey - Generate key (Owner only)\n"
        "/panel - Open Owner Panel (Owner only)"
    )


async def panel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_user.id != ADMIN_ID:
        await update.effective_message.reply_text(
            "❌ Owner access only."
        )
        return

    await update.effective_message.reply_text(
        "👑 YAGAMI OWNER PANEL",
        reply_markup=owner_menu()
    )


# ==============================
# BOT STARTUP
# ==============================

async def run_bot():
    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("panel", panel_command))
    app.add_handler(CommandHandler("newkey", newkey))

    app.add_handler(CommandHandler("addcodm", addcodm))
    app.add_handler(CommandHandler("addml", addml))
    app.add_handler(CommandHandler("delitem", delete_item))

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            reject_documents
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            check_key
        )
    )

    initialized = False
    started = False
    polling = False

    try:
        await app.initialize()
        initialized = True

        await app.start()
        started = True

        await app.updater.start_polling(
            drop_pending_updates=True
        )
        polling = True

        print("YAGAMI BOT is running successfully!")

        await asyncio.Event().wait()

    finally:
        if polling:
            await app.updater.stop()

        if started:
            await app.stop()

        if initialized:
            await app.shutdown()


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing.")

    if ADMIN_ID <= 0:
        raise ValueError("ADMIN_ID is missing or invalid.")

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
    
