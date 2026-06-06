"""
✅ JOIN REQUEST BOT — Python 3.11 + python-telegram-bot 20.7
"""
import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    ContextTypes,
)

BOT_TOKEN  = os.environ.get("BOT_TOKEN", "8871745549:AAGjU4ieXckOXNi3qzCsO64JAUMlmujiVLw")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-3966932396"))
ADMIN_IDS  = [int(x) for x in os.environ.get("ADMIN_IDS", "8043292489").split(",")]

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

approved_count = 0

async def handle_join_request(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    global approved_count
    request = update.chat_join_request
    user = request.from_user
    try:
        await ctx.bot.approve_chat_join_request(
            chat_id=request.chat.id,
            user_id=user.id
        )
        approved_count += 1
        logger.info(f"Tasdiqlandi: {user.full_name} ({user.id})")

        try:
            await ctx.bot.send_message(
                user.id,
                "Arizangiz tasdiqlandi!\n\nKanalga muvaffaqiyatli qo'shildingiz. Xush kelibsiz!"
            )
        except Exception:
            pass

        for aid in ADMIN_IDS:
            try:
                uname = f"@{user.username}" if user.username else "yo'q"
                await ctx.bot.send_message(
                    aid,
                    f"Yangi a'zo!\n"
                    f"Ism: {user.full_name}\n"
                    f"Username: {uname}\n"
                    f"ID: {user.id}\n"
                    f"Jami tasdiqlangan: {approved_count}"
                )
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Xato: {e}")

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in ADMIN_IDS:
        await update.message.reply_text(
            f"Admin panel\n\nTasdiqlangan: {approved_count}\n\nBot ishlayapti!"
        )
    else:
        await update.message.reply_text(
            "Bot ishlayapti!\nKanalga ariza yuboring — avtomatik tasdiqlanadi."
        )

async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    await update.message.reply_text(f"Tasdiqlangan: {approved_count}")

def main():
    print(f"Bot ishga tushdi! Admin: {ADMIN_IDS}, Kanal: {CHANNEL_ID}")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
