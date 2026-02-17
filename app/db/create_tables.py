import asyncio
from sqlalchemy.exc import OperationalError
from app.db.base import Base
from app.db.session import engine
import app.db.models

async def create_all_tables(retries: int = 10, delay: int = 2):
    """
    Try to create all tables. If the DB is not ready yet, retry a few times.
    """
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created successfully")
            return
        except OperationalError:
            print(f"Database not ready, retrying in {delay}s... ({attempt}/{retries})")
            await asyncio.sleep(delay)
    raise RuntimeError("❌ Failed to create tables after multiple retries")

if __name__ == "__main__":
    asyncio.run(create_all_tables())

