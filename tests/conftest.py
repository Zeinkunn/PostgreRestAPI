import pytest
import psycopg
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.config import settings
from app.database import get_db
from app.models import Base, AgentMemory, GeneralData

# Setup a test database name
TEST_DB_NAME = "postgres_test"
TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{TEST_DB_NAME}"

# Session-scoped fixture to setup the test database
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Connect to default database to create the test database
    try:
        with psycopg.connect(
            f"dbname={settings.DB_NAME} user={settings.DB_USER} password={settings.DB_PASS} host={settings.DB_HOST} port={settings.DB_PORT}",
            autocommit=True
        ) as conn:
            conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
            conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    except Exception as e:
        print(f"Error creating test database: {e}")
        
    # Ensure pgvector is active in the test database
    try:
        with psycopg.connect(
            f"dbname={TEST_DB_NAME} user={settings.DB_USER} password={settings.DB_PASS} host={settings.DB_HOST} port={settings.DB_PORT}",
            autocommit=True
        ) as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    except Exception as e:
        print(f"Error creating vector extension: {e}")

    yield
    
    # Teardown: Drop the test database after the session is fully completed
    try:
        with psycopg.connect(
            f"dbname={settings.DB_NAME} user={settings.DB_USER} password={settings.DB_PASS} host={settings.DB_HOST} port={settings.DB_PORT}",
            autocommit=True
        ) as conn:
            # Drop connections if any are lingering
            conn.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid()")
            conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    except Exception as e:
        pass

# Create an async engine connected safely to the test DB
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(class_=AsyncSession, bind=test_engine, expire_on_commit=False)

# Before each test, drop and recreate tables for a clean slate
@pytest.fixture(autouse=True)
async def setup_test_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Override the get_db dependency to point to the test db
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Fixture to provide an AsyncClient for test requests
@pytest.fixture
async def async_client():
    # Use ASGITransport to bypass networking layer for rapid testing
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

# Common Fixtures for Payloads
@pytest.fixture
def auth_headers():
    return {"x-api-key": settings.API_KEY}

@pytest.fixture
def dummy_embedding():
    # A generic 768-D normalized embedding vector
    return [0.1] * 768

@pytest.fixture
async def seed_memory():
    async with TestingSessionLocal() as session:
        memory = AgentMemory(
            persona_id="persona_alpha",
            content="This is a test memory context.",
            embedding=[0.2] * 768
        )
        session.add(memory)
        await session.commit()
        await session.refresh(memory)
        return memory

@pytest.fixture
async def seed_data():
    async with TestingSessionLocal() as session:
        data = GeneralData(
            title="Sample Title",
            description="Sample Description",
            payload={"key": "value"}
        )
        session.add(data)
        await session.commit()
        await session.refresh(data)
        return data

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
