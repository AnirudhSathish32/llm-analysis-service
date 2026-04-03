import asyncio
import logging
from sqlalchemy import text
from app.db.session import engine

logger = logging.getLogger(__name__)

async def test_connection():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("Connection successful, result: %s", result.scalar())
    except Exception as e:
        logger.error("Connection failed: %s", e)

if __name__ == "__main__":
    asyncio.run(test_connection())
