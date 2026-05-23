import asyncio
import logging
import signal

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.config import TELEGRAM_TOKEN, ADMIN_BOT_TOKEN, BUOI_CONFIG
from app.database.connection import init_pool, close_pool
from app.database.init_db import init_db
import app.database.crud as crud
from app.handlers import student, admin

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def build_student_app() -> Application:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start",    student.start))
    app.add_handler(CommandHandler("dangky",   student.dangky))
    app.add_handler(CommandHandler("xoa",      student.xoa_cmd))
    app.add_handler(CommandHandler("bangdiem", student.bangdiem_cmd))
    # WebApp data phải đứng trước TEXT để được ưu tiên
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, student.xu_ly_ket_qua_webapp))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, student.handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, student.handle_photo))
    app.add_error_handler(student.error_handler)
    return app


def build_admin_app() -> Application:
    app = Application.builder().token(ADMIN_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",     admin.start))
    app.add_handler(CommandHandler("broadcast", admin.broadcast_cmd))
    app.add_handler(CommandHandler("truyna",    admin.truyna_cmd))
    app.add_handler(CommandHandler("nangluc",   admin.nangluc_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin.handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, admin.handle_photo))
    app.add_error_handler(admin.error_handler)
    return app


async def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("Thiếu TELEGRAM_TOKEN trong .env")
    if not ADMIN_BOT_TOKEN:
        raise ValueError("Thiếu ADMIN_BOT_TOKEN trong .env")

    # Khởi tạo DB một lần dùng chung cho cả 2 bot
    logger.info("Đang kết nối database...")
    await init_pool()
    await init_db()
    for so_buoi, info in BUOI_CONFIG.items():
        try:
            await crud.upsert_lesson(so_buoi, info["ten"])
        except Exception as e:
            logger.warning(f"Seed lesson {so_buoi}: {e}")

    student_app = build_student_app()
    admin_app = build_admin_app()

    async with student_app, admin_app:
        await student_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        await admin_app.updater.start_polling(allowed_updates=["message"])

        logger.info("✅ Student bot & Admin bot đang chạy!")

        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, stop.set)
            except (NotImplementedError, RuntimeError):
                pass  # Windows không hỗ trợ add_signal_handler

        await stop.wait()

        logger.info("Đang dừng bots...")
        await student_app.updater.stop()
        await admin_app.updater.stop()

    await close_pool()
    logger.info("Đã dừng hoàn toàn.")


if __name__ == "__main__":
    asyncio.run(main())
