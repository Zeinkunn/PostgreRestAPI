import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event, text
from pgvector.asyncpg import register_vector
from app.config import settings
from app.models import Base
import psycopg

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
        # Create vector extension using a raw thread-blocking connection because it must
        # be completed before any async listener registers the type.
        with psycopg.connect(
            f"dbname={settings.DB_NAME} user={settings.DB_USER} password={settings.DB_PASS} host={settings.DB_HOST} port={settings.DB_PORT}",
            autocommit=True
        ) as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Start using alembic for schema migrations instead of create_all
        logger.info("Database vector extension checked/initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# Event listener registers vector type automatically on new connections
@event.listens_for(engine.sync_engine, "connect")
def connect(dbapi_connection, connection_record):
    dbapi_connection.run_async(register_vector)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
