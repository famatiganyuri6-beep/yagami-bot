
import os
import io
import sqlite3
import secrets
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =====================================
# CONFIGURATION
# =====================================

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

DB_PATH = os.environ.get("DATABASE_PATH", "yagami.db")

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


# =====================================
# DATABASE
# =====================================

def connect_db():
    return sqlite3.connect(DB_PATH, timeout=20)


def initialize_database():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS access_keys (
                key_hash TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game TEXT NOT NULL,
                label TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def hash_key(value):
    return hashlib.sha256(value.encode()).hexdigest()


def is_owner(user_id):
    return user_id == ADMIN_ID


def is_authorized(user_id):
    if is_owner(user_id):
        return True

    with connect_db() as conn:
        result = conn.execute(
            "SELECT 1 FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

    return result is not None


# =====================================
# KEY SYSTEM
# =====================================

def generate_key():
    return "YAGAMI-" + secrets.token_hex(4).upper()


def create_key():
    key = generate_key()

    with connect_db() as conn:
        conn.execute(
            "INSERT INTO access_keys VALUES (?, ?)",
            (hash_key(key), timestamp())
        )

    return key


def redeem_key(user_id, key):
    with connect_db() as conn:
        result = conn.execute(
            "SELECT 1 FROM access_keys WHERE key_hash = ?",
            (hash_key(key.strip()),)
        ).fetchone()

        if not result:
            return False

        conn.execute(
            "DELETE FROM access_keys WHERE key_hash = ?",
            (hash_key(key.strip()),)
        )

        conn.execute(
            "INSERT OR IGNORE INTO users VALUES (?, ?)",
            (user_id, timestamp())
        )

    return True


# =====================================
# MAIN KEYBOARD
# =====================================

def main_menu(owner=False):
    buttons = [
        ["📂 GENERATE FILES", "📊 MY STATISTICS"],
        ["🔑 REDEEM KEY", "🎮 CODM TXT"],
        ["🔥 ML TXT", "🔐 SECURITY TOOLS"],
    ]

    if owner:
        buttons.append(["👑 OWNER PANEL"])

    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )


# =====================================
# OWNER PANEL
# =====================================

def owner_menu():
    buttons = [
        [
            InlineKeyboardButton(
                "📂 GENERATE FILES",
                callback_data="generate"
            ),
            InlineKeyboardButton(
                "📊 MY STATISTICS",
                callback_data="stats"
            )
        ],
        [
            InlineKeyboardButton(
                "🔑 GENERATE KEY",
                callback_data="genkey"
            ),
            InlineKeyboardButton(
                "👥 MANAGE USERS",
                callback_data="users"
            )
        ],
        [
            InlineKeyboardButton(
                "🎮 CODM CATALOG",
                callback_data="codm"
            ),
            InlineKeyboardButton(
                "🔥 ML CATALOG",
                callback_data="ml"
            )
        ],
        [
            InlineKeyboardButton(
                "📁 CATALOG MANAGEMENT",
                callback_data="catalog"
            )
        ],
        [
            InlineKeyboardButton(
                "🔒 SECURITY SETTINGS",
                callback_data="security"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ BACK TO MENU",
                callback_data="home"
            )
        ]
    ]

    return InlineKeyboardMarkup(buttons)


# =====================================
# START
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_owner(user_id):
        await update.effective_message.reply_text(
            "👑 WELCOME TO YAGAMI BOT, OWNER!\n\n"
            "All owner controls are available below.",
            reply_markup=main_menu(True)
        )

    elif is_authorized(user_id):
        await update.effective_message.reply_text(
            "👋 WELCOME TO YAGAMI BOT!",
            reply_markup=main_menu(False)
        )

    else:
        context.user_data["waiting_key"] = True

        await update.effective_message.reply_text(
            "🔒 ACCESS REQUIRED\n\n"
            "This bot is private.\n"
            "Enter your Entrance Key to continue."
        )


# =====================================
# GENERATE KEY
# =====================================

async def generate_new_key(update, context):
    if not is_owner(update.effective_user.id):
        await update.effective_message.reply_text(
            "❌ Owner access only."
        )
        return

    key = create_key()

    await update.effective_message.reply_text(
        "🔑 NEW ENTRANCE KEY\n\n"
        f"{key}\n\n"
        "This key can only be redeemed once."
    )


# =====================================
# REDEEM KEY
# =====================================

async def redeem_command(update, context):
    user_id = update.effective_user.id

    if is_authorized(user_id):
        await update.effective_message.reply_text(
            "✅ You already have access."
        )
        return

    context.user_data["waiting_key"] = True

    await update.effective_message.reply_text(
        "🔑 REDEEM KEY\n\n"
        "Please enter your Entrance Key."
    )


# =====================================
# ACCOUNT CATALOG
# =====================================

async def show_catalog(message, game):
    with connect_db() as conn:
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
            f"📁 {game} ACCOUNT CATALOG\n\n"
            "No catalog entries available."
        )
        return

    lines = [
        f"📁 {game} ACCOUNT CATALOG",
        ""
    ]

    for item_id, label in rows:
        lines.append(f"#{item_id} - {label}")

    lines.extend([
        "",
        "🔒 Private login credentials are never displayed."
    ])

    await message.reply_text("\n".join(lines))


# =====================================
# ADD CATALOG ENTRY
# =====================================

async def add_catalog(update, context, game):
    if not is_owner(update.effective_user.id):
        await update.effective_message.reply_text(
            "❌ Owner access only."
        )
        return

    label = " ".join(context.args).strip()

    blocked = (
        "password", "passwd", "login",
        "token", "email", "credential"
    )

    if (
        not label
        or len(label) > 60
        or "@" in label
        or any(word in label.lower() for word in blocked)
    ):
        await update.effective_message.reply_text(
            "❌ Enter a valid non-sensitive account label."
        )
        return

    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO catalog (game, label, created_at)
            VALUES (?, ?, ?)
            """,
            (game, label, timestamp())
        )

    await update.effective_message.reply_text(
        f"✅ {game} catalog entry added!\n\n"
        f"Account Label: {label}"
    )


async def add_codm(update, context):
    await add_catalog(update, context, "CODM")


async def add_ml(update, context):
    await add_catalog(update, context, "ML")


# =====================================
# DELETE CATALOG ENTRY
# =====================================

async def delete_catalog(update, context):
    if not is_owner(update.effective_user.id):
        await update.effective_message.reply_text(
            "❌ Owner access only."
        )
        return

    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text(
            "Usage: /delete 1"
        )
        return

    item_id = int(context.args[0])

    with connect_db() as conn:
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
            "❌ Entry not found."
        )


# =====================================
# GENERATE SAFE CATALOG FILE
# =====================================

async def generate_file(message):
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT game, id, label
            FROM catalog
            ORDER BY game, id
            """
        ).fetchall()

    if not rows:
        await message.reply_text(
            "📂 No catalog entries available."
        )
        return

    output = ["YAGAMI BOT ACCOUNT CATALOG", ""]

    for game, item_id, label in rows:
        output.append(f"{game} | ID: {item_id} | {label}")

    output.extend([
        "",
        "This export contains non-sensitive labels only."
    ])

    file_data = io.BytesIO(
        "\n".join(output).encode("utf-8")
    )

    file_data.name = "yagami_catalog.txt"

    await message.reply_document(
        document=file_data,
        caption="📂 YAGAMI BOT CATALOG EXPORT"
    )


# =====================================
# STATISTICS
# =====================================

async def show_statistics(message):
    with connect_db() as conn:
        users = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        keys = conn.execute(
            "SELECT COUNT(*) FROM access_keys"
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
        f"🔑 Available Keys: {keys}\n"
        f"🎮 CODM Entries: {codm}\n"
        f"🔥 ML Entries: {ml}"
    )


# =====================================
# USER MANAGEMENT
# =====================================

async def show_users(message):
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT user_id FROM users
            ORDER BY created_at DESC
            LIMIT 30
            """
        ).fetchall()

    lines = ["👥 AUTHORIZED USERS", ""]

    for row in rows:
        lines.append(f"• {row[0]}")

    if not rows:
        lines.append("No authorized users.")

    await message.reply_text("\n".join(lines))


async def revoke_user(update, context):
    if not is_owner(update.effective_user.id):
        await update.effective_message.reply_text(
            "❌ Owner access only."
        )
        return

    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text(
            "Usage: /revoke USER_ID"
        )
        return

    target = int(context.args[0])

    if target == ADMIN_ID:
        await update.effective_message.reply_text(
            "❌ The owner cannot be removed."
        )
        return

    with connect_db() as conn:
        cursor = conn.execute(
            "DELETE FROM users WHERE user_id = ?",
            (target,)
        )

    await update.effective_message.reply_text(
        "✅ User access revoked."
        if cursor.rowcount
        else "❌ User not found."
    )


# =====================================
# BUTTON HANDLER
# =====================================

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if not is_authorized(user_id):
        await query.message.reply_text(
            "🔒 Access denied."
        )
        return

    if data == "home":
        await query.message.reply_text(
            "🏠 MAIN MENU",
            reply_markup=main_menu(is_owner(user_id))
        )

    elif data == "panel":
        if not is_owner(user_id):
            return

        await query.message.reply_text(
            "👑 YAGAMI OWNER PANEL",
            reply_markup=owner_menu()
        )

    elif data == "genkey":
        if not is_owner(user_id):
            return

        key = create_key()

        await query.message.reply_text(
            f"🔑 NEW ENTRANCE KEY\n\n{key}"
        )

    elif data == "generate":
        await generate_file(query.message)

    elif data == "stats":
        await show_statistics(query.message)

    elif data == "users":
        if is_owner(user_id):
            await show_users(query.message)

    elif data == "codm":
        await show_catalog(query.message, "CODM")

    elif data == "ml":
        await show_catalog(query.message, "ML")

    elif data == "catalog":
        if is_owner(user_id):
            await query.message.reply_text(
                "📁 CATALOG MANAGEMENT\n\n"
                "/addcodm Account 001\n"
                "/addml Account 001\n"
                "/delete 1\n\n"
                "Use non-sensitive labels only."
            )

    elif data == "security":
        if is_owner(user_id):
            await query.message.reply_text(
                "🔒 SECURITY SETTINGS\n\n"
                "• Owner-only administration\n"
                "• Single-use entrance keys\n"
                "• Persistent authorization database\n"
                "• No credential exports\n"
                "• File uploads disabled"
            )


# =====================================
# TEXT HANDLER
# =====================================

async def text_handler(update, context):
    user_id = update.effective_user.id
    text = update.effective_message.text.strip()

    if not is_authorized(user_id):
        if context.user_data.get("waiting_key"):
            if redeem_key(user_id, text):
                context.user_data["waiting_key"] = False

                await update.effective_message.reply_text(
                    "✅ KEY ACCEPTED!\n\n"
                    "Welcome to YAGAMI BOT.",
                    reply_markup=main_menu(False)
                )
            else:
                await update.effective_message.reply_text(
                    "❌ Invalid or already used key."
                )
        else:
            await update.effective_message.reply_text(
                "🔒 Access denied. Use /start to enter your key."
            )
        return

    if text == "📂 GENERATE FILES":
        await generate_file(update.effective_message)

    elif text == "📊 MY STATISTICS":
        await show_statistics(update.effective_message)

    elif text == "🔑 REDEEM KEY":
        await redeem_command(update, context)

    elif text == "🎮 CODM TXT":
        await show_catalog(update.effective_message, "CODM")

    elif text == "🔥 ML TXT":
        await show_catalog(update.effective_message, "ML")

    elif text == "🔐 SECURITY TOOLS":
        await update.effective_message.reply_text(
            "🔐 SECURITY CENTER\n\n"
            "Credential distribution and automated "
            "account-access tools are disabled."
        )

    elif text == "👑 OWNER PANEL":
        if is_owner(user_id):
            await update.effective_message.reply_text(
                "👑 YAGAMI OWNER PANEL",
                reply_markup=owner_menu()
            )

    else:
        await update.effective_message.reply_text(
            "Please select an option from the menu."
        )


# =====================================
# DOCUMENT HANDLER
# =====================================

async def reject_documents(update, context):
    await update.effective_message.reply_text(
        "🔒 File uploads are disabled.\n\n"
        "Use the non-sensitive account catalog instead."
    )


# =====================================
# HELP
# =====================================

async def help_command(update, context):
    await update.effective_message.reply_text(
        "❓ YAGAMI BOT HELP\n\n"
        "/start - Start bot\n"
        "/panel - Owner panel\n"
        "/newkey - Generate entrance key\n"
        "/addcodm - Add CODM catalog label\n"
        "/addml - Add ML catalog label\n"
        "/delete - Delete catalog entry\n"
        "/revoke - Revoke user access"
    )


async def panel_command(update, context):
    if not is_owner(update.effective_user.id):
        await update.effective_message.reply_text(
            "❌ Owner access only."
        )
        return

    await update.effective_message.reply_text(
        "👑 YAGAMI OWNER PANEL",
        reply_markup=owner_menu()
    )


# =====================================
# MAIN
# =====================================

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing.")

    if ADMIN_ID <= 0:
        raise ValueError("ADMIN_ID is missing.")

    initialize_database()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("panel", panel_command))
    app.add_handler(CommandHandler("newkey", generate_new_key))
    app.add_handler(CommandHandler("redeem", redeem_command))

    app.add_handler(CommandHandler("addcodm", add_codm))
    app.add_handler(CommandHandler("addml", add_ml))
    app.add_handler(CommandHandler("delete", delete_catalog))
    app.add_handler(CommandHandler("revoke", revoke_user))

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
            text_handler
        )
    )

    print("YAGAMI BOT is running successfully!")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
        
