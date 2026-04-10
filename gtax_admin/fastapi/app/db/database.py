"""
Async SQLAlchemy database configuration.

Demonstrates:
- Async database setup with SQLAlchemy 2.0
- Session factory pattern
- Context managers for session handling
- Dependency injection with generators
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    All models should inherit from this class to be
    automatically registered with the ORM.
    """
    pass


# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Maximum overflow connections
)

# Session factory for creating database sessions
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    
    Demonstrates:
    - Async context manager protocol
    - Proper resource cleanup
    - Transaction handling
    
    Example:
        >>> async with get_session() as session:
        ...     result = await session.execute(query)
    
    Yields:
        AsyncSession: Database session for executing queries
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error("Database session error", error=str(e))
        raise
    finally:
        await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    This is designed to be used with FastAPI's Depends() for
    automatic dependency injection.
    
    Example:
        >>> @router.get("/users")
        ... async def get_users(db: AsyncSession = Depends(get_db)):
        ...     ...
    
    Yields:
        AsyncSession: Database session for the request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This should be called during application startup
    to ensure all tables exist.
    """
    async with engine.begin() as conn:
        # Import all models to register them with Base
        from app.models import user, project, task  # noqa: F401
        
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def close_db() -> None:
    """
    Close database connections.
    
    This should be called during application shutdown
    to properly clean up resources.
    """
    await engine.dispose()
    logger.info("Database connections closed")
