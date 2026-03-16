import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event, text
from pgvector.asyncpg import register_vector
from app.config import settings
from app.models import Base
from app.models import Base
import asyncpg
logger = logging.getLogger(__name__)

# Async Engine Setup
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Async Session Maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def init_db():
    try:
        # Gunakan koneksi asyncpg langsung untuk setup pgvector
        # karena harus dilakukan sebelum SQLAlchemy engine digunakan
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASS,
            database=settings.DB_NAME,
        )
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await register_vector(conn)
        await conn.close()
        logger.info("Database vector extension checked/initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
