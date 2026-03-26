from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import config

DATABASE_URL = config.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# produces/generates new async sessions for queries
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()


async def init_db() -> None:
    """Creates all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )  # create all tables in the database


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for async DB operations"""
    async with async_session_factory() as session:
        # Creates a new async session, automatically closed at the end.
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
