import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.config import TELEGRAM_TOKEN, BUOI_CONFIG, BASE_DOMAIN
from app.database.connection import init_pool, close_pool
from app.database.init_db import init_db
import app.database.crud as crud
from app.handlers import student

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Version tag — cập nhật mỗi khi deploy để dễ verify
BOT_VERSION = "2026-domain-fixed"


async def post_init(app: Application):
    await init_pool()
    await init_db()
    for so_buoi, info in BUOI_CONFIG.items():
        try:
            await crud.upsert_lesson(so_buoi, info["ten"])
        except Exception as e:
            logger.warning(f"Error seeding lesson {so_buoi}: {e}")
    logger.info(f"✅ Bot khởi động — version: {BOT_VERSION}")


async def post_shutdown(app: Application):
    await close_pool()


async def ping(update: Update, context):
    """Debug: kiểm tra version + trạng thái đăng nhập."""
    uid = update.effective_user.id
    status = await student.check_web_status(uid)
    status_icon = {"approved": "✅", "pending": "⏳", "not_found": "❌", "rejected": "🚫"}.get(status, "❓")
    await update.message.reply_text(
        f"🏓 *Pong!*\n\n"
        f"🤖 Version: `{BOT_VERSION}`\n"
        f"📅 Deploy: `{datetime.now().strftime('%d/%m/%Y %H:%M')}`\n"
        f"🆔 Telegram ID: `{uid}`\n"
        f"🔐 Trạng thái: {status_icon} `{status}`\n\n"
        f"🌐 Web: `{BASE_DOMAIN}`\n"
        f"🔧 ENV: `{os.getenv('BASE_DOMAIN', 'NOT SET')}`",
        parse_mode="Markdown",
    )


def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("Thiếu TELEGRAM_TOKEN")

    app = (Application.builder()
           .token(TELEGRAM_TOKEN)
           .post_init(post_init)
           .post_shutdown(post_shutdown)
           .build())

    # Commands
    app.add_handler(CommandHandler("start",     student.start))
    app.add_handler(CommandHandler("dangky",    student.dangky))
    app.add_handler(CommandHandler("xoa",       student.xoa_cmd))
    app.add_handler(CommandHandler("btvn",      student.btvn_cmd))
    app.add_handler(CommandHandler("chonbuoi",  student.chonbuoi_cmd))
    app.add_handler(CommandHandler("bangdiem",  student.bangdiem_cmd))
    app.add_handler(CommandHandler("ping",      ping))

    # WebApp kết quả bài tập (phải đứng TRƯỚC handler TEXT)
    app.add_handler(MessageHandler(
        filters.StatusUpdate.WEB_APP_DATA,
        student.xu_ly_ket_qua_webapp,
    ))

    # Text & Photo
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, student.handle_message))
    app.add_handler(MessageHandler(filters.PHOTO,                   student.handle_photo))

    app.add_error_handler(student.error_handler)

    logger.info("VInaStudy Student Bot đang chạy...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
