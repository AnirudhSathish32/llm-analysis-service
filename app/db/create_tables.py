import asyncio
import app.db.models
from app.db.base import Base
from app.db.session import engine
from app.db.models import AnalysisRequest, AnalysisResult

async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_all_tables())
    print("Tables created successfully")
