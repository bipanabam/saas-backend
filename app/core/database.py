from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, LoaderCriteriaOption, with_loader_criteria

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


class Base(DeclarativeBase):
    pass


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


def tenant_filter_option() -> LoaderCriteriaOption:
    """Returns a SQLAlchemy loader option to filter queries by the current tenant ID."""
    from app.core.tenant_context import get_current_tenant_id
    from app.models import Tenant

    return with_loader_criteria(
        Tenant, lambda cls: cls.id == get_current_tenant_id(), include_aliases=True
    )
