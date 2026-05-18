from sqlalchemy.ext.asyncio import AsyncEngine
from app.db.session import Base, engine
from app.models import user, chat, message, file

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
