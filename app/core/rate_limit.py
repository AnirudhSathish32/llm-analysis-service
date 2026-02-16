from fastapi import HTTPException, Request
from app.cache.redis import redis_client

RATE_LIMIT = 20  # requests
WINDOW_SECONDS = 60

async def rate_limiter(request: Request):
    key = f"rate:{request.client.host}"
    current = await redis_client.incr(key)

    if current == 1:
        await redis_client.expire(key, WINDOW_SECONDS)

    if current > RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
