import asyncio
from sqlalchemy import text
from app.db.session import engine

async def test_connection():
    try:
        async with engine.begin() as conn:
            # Use text() to wrap the SQL query
            result = await conn.execute(text("SELECT 1"))
            print("Connection successful, result:", result.scalar())
    except Exception as e:
        print("Connection failed:", e)

if __name__ == "__main__":
    asyncio.run(test_connection())