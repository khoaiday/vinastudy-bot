import asyncio
import asyncpg
import logging
from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Global connection pool
_pool = None

async def init_pool():
    global _pool
    if _pool is not None:
        return
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL chưa được cấu hình")
        return

    # Retry tối đa 5 lần (Railway PostgreSQL đôi khi khởi động chậm hơn web service)
    for attempt in range(1, 6):
        try:
            _pool = await asyncpg.create_pool(
                dsn=DATABASE_URL,
                min_size=1,
                max_size=10,
                max_inactive_connection_lifetime=300,  # tái tạo connection idle > 5 phút
                command_timeout=30,                    # query timeout
            )
            logger.info(f"✅ Database pool created (attempt {attempt})")
            return
        except Exception as e:
            logger.error(f"❌ Pool init attempt {attempt}/5 failed: {e}")
            if attempt < 5:
                await asyncio.sleep(2 ** attempt)  # backoff: 2s, 4s, 8s, 16s

    logger.error("❌ Không thể kết nối database sau 5 lần thử")

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("✅ Database connection pool closed")

def get_pool():
    return _pool
