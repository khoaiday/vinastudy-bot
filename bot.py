import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.config import TELEGRAM_TOKEN, BUOI_CONFIG
from app.database.connection import init_pool, close_pool
from app.database.init_db import init_db
import app.database.crud as crud
from app.handlers import student

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def post_init(app: Application):
    await init_pool()
    await init_db()
    for so_buoi, info in BUOI_CONFIG.items():
        try:
            await crud.upsert_lesson(so_buoi, info["ten"])
        except Exception as e:
            logger.warning(f"Error seeding lesson {so_buoi}: {e}")

async def post_shutdown(app: Application):
    await close_pool()

def main():
    if not TELEGRAM_TOKEN: raise ValueError("Thiếu TELEGRAM_TOKEN")
    
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()

    app.add_handler(CommandHandler("start",     student.start))
    app.add_handler(CommandHandler("dangky",    student.dangky))
    app.add_handler(CommandHandler("xoa",       student.xoa_cmd))
    app.add_handler(CommandHandler("btvn",      student.btvn_cmd))
    app.add_handler(CommandHandler("chonbuoi",  student.chonbuoi_cmd))
    app.add_handler(CommandHandler("bangdiem",  student.bangdiem_cmd))
    app.add_handler(MessageHandler(filters.TEXT  & ~filters.COMMAND, student.handle_message))
    app.add_handler(MessageHandler(filters.PHOTO,                    student.handle_photo))
    app.add_error_handler(student.error_handler)

    logger.info("VInaStudy Student Bot đang chạy (Async)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
