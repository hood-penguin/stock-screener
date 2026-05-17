"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from .config import get_settings

settings = get_settings()

# Convert standard postgresql:// to postgresql+asyncpg://
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
_pool_kwargs = (
    {}
    if settings.is_development
    else {"pool_size": settings.database_pool_size, "max_overflow": settings.database_max_overflow}
)
engine = create_async_engine(
    async_database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    poolclass=NullPool if settings.is_development else None,
    **_pool_kwargs,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncSession:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


get_db = get_db_session


async def init_db() -> None:
    """Initialize database (create tables)."""
    from .models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize screening criteria registry
    from .core.screening import CriteriaRegistry
    CriteriaRegistry.discover()


async def close_db() -> None:
    """Close database connection."""
    await engine.dispose()
