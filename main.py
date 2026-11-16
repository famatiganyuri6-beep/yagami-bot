import os, random, string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
keys = set()
ok = set()
def mk():
    return "YAGAMI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
def menu(a):
    b = [[InlineKeyboardButton("🎮 CODM TXT", callback_data="codm")],[InlineKeyboardButton("🔥 ML TXT", callback_data="ml")]]
    if a: b.append([InlineKeyboardButton("🔑 Generate Key", callback_data="genkey")])
    b.append([InlineKeyboardButton("❓ Help", callback_data="help")])
    return InlineKeyboardMarkup(b)
async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    i = u.effective_user.id
    if i == ADMIN_ID:
        ok.add(i)
        await u.message.reply_text("👑 Welcome to YAGAMI BOT, Admin!", reply_markup=menu(True))
    elif i not in ok:
        await u.message.reply_text("🔒 Welcome to YAGAMI BOT\n\nThis bot is LOCKED.\nPlease enter your Entrance Key:")
    else:
        await u.message.reply_text("👋 Welcome to YAGAMI BOT!", reply_markup=menu(False))
async def newkey(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID:
        await u.message.reply_text("❌ Only Admin can generate keys.")
        return
    k = mk(); keys.add(k)
    await u.message.reply_text(f"🔑 New Key:\n\n{k}")
async def codm(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("🎮 CODM TXT\n\nSend your CODM .txt file here.")
async def ml(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("🔥 ML TXT\n\nSend your ML .txt file here.")
async def hlp(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("❓ HELP\n\n1. Type /start\n2. Enter key\n3. Press CODM TXT or ML TXT")
async def btn(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    if q.data == "codm": await q.message.reply_text("🎮 CODM TXT\n\nSend your CODM .txt file here.")
    elif q.data == "ml": await q.message.reply_text("🔥 ML TXT\n\nSend your ML .txt file here.")
    elif q.data == "help": await q.message.reply_text("❓ HELP\n\nPress CODM TXT or ML TXT.")
    elif q.data == "genkey":
        if q.from_user.id != ADMIN_ID:
            await q.message.reply_text("❌ Only Admin can generate keys.")
            return
        k = mk(); keys.add(k)
        await q.message.reply_text(f"🔑 New Key:\n\n{k}")
async def chk(u: Update, c: ContextTypes.DEFAULT_TYPE):
    i = u.effective_user.id; t = u.message.text.strip()
    if i in ok or i == ADMIN_ID: return
    if t in keys:
        keys.remove(t); ok.add(i)
        await u.message.reply_text("✅ Key Accepted! Welcome to YAGAMI BOT!", reply_markup=menu(False))
    else: await u.message.reply_text("❌ Invalid Key. Try again:")
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newkey", newkey))
    app.add_handler(CommandHandler("codm", codm))
    app.add_handler(CommandHandler("ml", ml))
    app.add_handler(CommandHandler("help", hlp))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chk))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)
if __name__ == "__main__": main()
