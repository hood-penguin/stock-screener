import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient

from app.main import create_app
from app.database import Base, get_db
from app.config import settings


@pytest_asyncio.fixture
async def async_engine():
    """테스트용 인메모리 SQLite 엔진"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session_maker(async_engine):
    """테스트용 async session maker"""
    return async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def db_session(async_session_maker):
    """테스트용 DB 세션"""
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def test_app(async_session_maker):
    """테스트용 FastAPI 앱"""
    app = create_app()

    async def override_get_db():
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest_asyncio.fixture
async def async_client(test_app):
    """테스트용 AsyncClient"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_user_data():
    """테스트용 사용자 데이터"""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123",
    }


@pytest.fixture
def sample_stock_data():
    """테스트용 주식 데이터"""
    return {
        "ticker": "AAPL",
        "market": "US",
        "company_name": "Apple Inc.",
        "sector": "Technology",
    }
