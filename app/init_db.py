import asyncio
from .database import engine, Base

async def init_models():
    async with engine.begin() as conn:
        # Drop all tables if they exist
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    print("Initializing database...")
    asyncio.run(init_models())
    print("Database initialized successfully!")
