"""
Pytest configuration and fixtures for API tests.
"""
import os
import asyncio
from typing import Generator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app


# Override database URL for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """Create test database and tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_db) -> Generator[AsyncSession, None, None]:
    """Create a new database session for each test."""
    engine = test_db
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency for testing."""
    async def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "auth: mark test as authentication test"
    )
    config.addinivalue_line(
        "markers", "family: mark test as product family test"
    )
    config.addinivalue_line(
        "markers", "identity: mark test as product identity test"
    )
    config.addinivalue_line(
        "markers", "variant: mark test as product variant test"
    )
    config.addinivalue_line(
        "markers", "bundle: mark test as bundle component test"
    )
    config.addinivalue_line(
        "markers", "listing: mark test as platform listing test"
    )
    config.addinivalue_line(
        "markers", "inventory: mark test as inventory test"
    )
