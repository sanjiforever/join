"""
✅ JOIN REQUEST BOT
Kanalga qo'shilish arizalarini avtomatik tasdiqlaydi
pip install python-telegram-bot
"""
import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, ChatJoinRequestHandler,
    CallbackQueryHandler, ContextTypes
)

# ══════════════════════════════════════════
#  ⚙️ SOZLAMALAR
# ══════════════════════════════════════════
BOT_TOKEN  = os.environ.get("BOT_TOKEN", "8871745549:AAGjU4ieXckOXNi3qzCsO64JAUMlmujiVLw")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "3966932396"))  # Kanal ID
ADMIN_IDS  = [int(x) for x in os.environ.get("ADMIN_IDS", "8043292489").split(",")]

# Xabarlar
WELCOME_MSG = """✅ Arizangiz tasdiqlandi!

Kanalga muvaffaqiyatli qo'shildingiz.
Xush kelibsiz! 🎉"""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Statistika (xotirada)
stats = {"approved": 0, "declined": 0}

# ══════════════════════════════════════════
#  ✅ ARIZA TASDIQLASH
# ══════════════════════════════════════════
async def handle_join_request(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user
    chat = request.chat

    try:
        # Arizani tasdiqlash
        await ctx.bot.approve_chat_join_request(
            chat_id=chat.id,
            user_id=user.id
        )
        stats["approved"] += 1

        # Foydalanuvchiga xabar
        try:
            await ctx.bot.send_message(
                chat_id=user.id,
                text=WELCOME_MSG
            )
        except Exception:
            pass  # Foydalanuvchi botni bloklab qo'ygan bo'lishi mumkin

        # Adminga xabar
        name = user.full_name or str(user.id)
        username = f"@{user.username}" if user.username else "username yo'q"
        logger.info(f"✅ Tasdiqlandi: {name} ({user.id})")

        for admin_id in ADMIN_IDS:
            try:
                await ctx.bot.send_message(
                    admin_id,
                    f"✅ Yangi a'zo!\n\n"
                    f"👤 {name}\n"
                    f"🔗 {username}\n"
                    f"🆔 `{user.id}`\n\n"
                    f"📊 Jami tasdiqlangan: {stats['approved']}",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Ariza tasdiqlanmadi {user.id}: {e}")

# ══════════════════════════════════════════
#  🤖 BOTGA BUYRUQLAR
# ══════════════════════════════════════════
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    is_admin = uid in ADMIN_IDS

    if is_admin:
        txt = (
            f"👋 Admin sifatida kirgansiz!\n\n"
            f"📊 Statistika:\n"
            f"✅ Tasdiqlangan: {stats['approved']}\n\n"
            f"Bot ishlayapti — kanalga kelgan arizalar avtomatik tasdiqlanadi."
        )
        await update.message.reply_text(txt, reply_markup=admin_kb())
    else:
        await update.message.reply_text(
            "✅ Bot ishlayapti!\n\n"
            "Kanalga qo'shilish uchun ariza yuboring — avtomatik tasdiqlanadi."
        )

async def stats_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    await update.message.reply_text(
        f"📊 *Statistika*\n\n"
        f"✅ Tasdiqlangan: *{stats['approved']}*\n"
        f"❌ Rad etilgan: *{stats['declined']}*",
        parse_mode="Markdown"
    )

# ══════════════════════════════════════════
#  ⌨️ ADMIN KLAVIATURA
# ══════════════════════════════════════════
def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
    ])

async def btn(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "stats":
        await q.edit_message_text(
            f"📊 *Statistika*\n\n"
            f"✅ Tasdiqlangan: *{stats['approved']}*",
            parse_mode="Markdown",
            reply_markup=admin_kb()
        )

# ══════════════════════════════════════════
#  ▶️ ISHGA TUSHIRISH
# ══════════════════════════════════════════
def main():
    print(f"✅ Join Request Bot ishga tushdi!")
    print(f"📋 Admin IDs: {ADMIN_IDS}")
    print(f"📢 Channel ID: {CHANNEL_ID}")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
