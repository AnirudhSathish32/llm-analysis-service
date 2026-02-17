from fastapi import FastAPI
from app.api.routes import analysis, metrics
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import app.db.models
from contextlib import asynccontextmanager

app = FastAPI(title=settings.app_name)

app.include_router(analysis.router)
app.include_router(metrics.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup logic ----
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # shutdown logic here 




app = FastAPI(lifespan=lifespan)
