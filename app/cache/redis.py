import logging
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


async def connect() -> None:
    """Verify Redis connection is healthy."""
    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except redis.ConnectionError as err:
        logger.error("Failed to connect to Redis: %s", err)
        raise


async def close() -> None:
    """Close the Redis connection pool."""
    await redis_client.aclose()
    logger.info("Redis connection closed")
