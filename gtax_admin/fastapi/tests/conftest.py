"""
Pytest configuration and fixtures.

This module provides shared fixtures for all tests.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.core.config import settings
from app.models.user import User, UserRole
from app.core.security import security_service


# Test database URL (use SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    
    Creates tables before each test and drops them after.
    """
    # Create test engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    # Create session factory
    TestSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with overridden database dependency.
    """
    # Override the database dependency
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """
    Create a test user.
    """
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=security_service.hash_password("TestPass123"),
        full_name="Test User",
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(test_db: AsyncSession) -> User:
    """
    Create an admin test user.
    """
    user = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password=security_service.hash_password("AdminPass123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """
    Generate authentication headers for test user.
    """
    token_data = {
        "sub": str(test_user.id),
        "email": test_user.email,
        "role": test_user.role.value
    }
    access_token = security_service.create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def admin_auth_headers(admin_user: User) -> dict:
    """
    Generate authentication headers for admin user.
    """
    token_data = {
        "sub": str(admin_user.id),
        "email": admin_user.email,
        "role": admin_user.role.value
    }
    access_token = security_service.create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}
