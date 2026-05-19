import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.config import ADMIN_BOT_TOKEN, BUOI_CONFIG
from app.database.connection import init_pool, close_pool
from app.database.init_db import init_db
import app.database.crud as crud
from app.handlers import admin

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
    if not ADMIN_BOT_TOKEN: raise ValueError("Thiếu ADMIN_BOT_TOKEN")

    app = Application.builder().token(ADMIN_BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()
    
    app.add_handler(CommandHandler("start",     admin.start))
    app.add_handler(CommandHandler("broadcast", admin.broadcast_cmd))
    app.add_handler(MessageHandler(filters.TEXT  & ~filters.COMMAND, admin.handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, admin.handle_photo))
    app.add_error_handler(admin.error_handler)

    logger.info("VInaStudy Admin Bot đang chạy (Async)...")
    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()
