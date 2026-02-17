from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.api.routes import analysis, metrics
from app.core.config import settings

# Import the create_all_tables function from your script
from app.db.create_tables import create_all_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Call your existing create_tables.py logic
    for _ in range(10):
        try:
            await create_all_tables()
            print("✅ Tables created successfully")
            break
        except Exception:
            print("DB not ready, retrying in 2s...")
            await asyncio.sleep(2)
    else:
        raise RuntimeError("Failed to create tables after retries")

    yield  # startup complete
    # shutdown logic here if needed

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(analysis.router)
app.include_router(metrics.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
