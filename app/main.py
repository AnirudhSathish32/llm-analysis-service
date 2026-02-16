from fastapi import FastAPI
from app.api.routes import analysis, metrics
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(analysis.router)
app.include_router(metrics.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
