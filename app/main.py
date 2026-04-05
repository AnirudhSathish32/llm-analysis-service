from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import uuid
import logging
import os

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


frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.isdir(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the SPA frontend. All non-API routes return index.html."""
        return FileResponse(os.path.join(frontend_dist, "index.html"))
