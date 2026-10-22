from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from .config import settings

# In Phase 4 with Docker, this will connect to the PostgreSQL container.
# For local testing before Docker, we'll use a local sqlite fallback if postgres isn't running,
# but the architecture is strictly SQLAlchemy Async.
DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"

# Use a fallback for local testing if needed
# DATABASE_URL = "sqlite+aiosqlite:///./enterprise_memory.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
