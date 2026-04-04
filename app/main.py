from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import asyncio
import uuid
import logging

from app.api.routes import analysis, metrics, documents
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.create_tables import create_all_tables
from app.cache import redis as redis_cache

logger = logging.getLogger(__name__)

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    for _ in range(10):
        try:
            await create_all_tables()
            logger.info("Tables created successfully")
            break
        except Exception:
            logger.warning("DB not ready, retrying in 2s...")
            await asyncio.sleep(2)
    else:
        raise RuntimeError("Failed to create tables after retries")

    await redis_cache.connect()

    yield

    await redis_cache.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(analysis.router)
app.include_router(metrics.router)
app.include_router(documents.router)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint. Returns OK if the service is running."""
    return {"status": "ok"}
