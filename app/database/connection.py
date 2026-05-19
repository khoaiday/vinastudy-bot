import asyncpg
import logging
from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Global connection pool
_pool = None

async def init_pool():
    global _pool
    if _pool is None and DATABASE_URL:
        try:
            _pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=10)
            logger.info("✅ Database connection pool created")
        except Exception as e:
            logger.error(f"❌ Failed to create pool: {e}")

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("✅ Database connection pool closed")

def get_pool():
    return _pool
