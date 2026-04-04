import logging
from fastapi import HTTPException, Request
from app.cache.redis import redis_client

RATE_LIMIT = 20
WINDOW_SECONDS = 60

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host


async def rate_limiter(request: Request) -> None:
    client_ip = get_client_ip(request)
    key = f"rate:{client_ip}"
    try:
        current = await redis_client.incr(key)

        if current == 1:
            await redis_client.expire(key, WINDOW_SECONDS)

        if current > RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Rate limiter Redis error, allowing request")
