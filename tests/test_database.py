import pytest
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.database import get_db
from app.models import AgentMemory, GeneralData
from app.config import settings

@pytest.mark.asyncio
async def test_engine_connects_successfully(db_session: AsyncSession):
    # Test that async engine can connect to PostgreSQL successfully
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.asyncio
async def test_get_db_yields_valid_session():
    # Test that `get_db()` dependency yields a valid `AsyncSession`
    session_generator = get_db()
    session = await session_generator.__anext__()
    assert isinstance(session, AsyncSession)
    assert session.is_active
    await session.close()

@pytest.mark.asyncio
async def test_connection_closes_properly():
    # Test that connection closes properly after session ends
    from tests.conftest import TestingSessionLocal
    async with TestingSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    # After the block, session has released the connection
    assert not session.in_transaction()

@pytest.mark.asyncio
async def test_wrong_db_credentials_fail_fast():
    # Test behavior when DB credentials are wrong -> raise error, don't hang
    from sqlalchemy.ext.asyncio import create_async_engine
    bad_url = f"postgresql+asyncpg://wronguser:wrongpass@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    bad_engine = create_async_engine(bad_url, connect_args={"timeout": 2})
    
    with pytest.raises(Exception) as exc_info:
        async with bad_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    
    # Should be some form of auth failure or connection error
    assert "password authentication failed" in str(exc_info.value) or "connect" in str(exc_info.value).lower()
    await bad_engine.dispose()

@pytest.mark.asyncio
async def test_unreachable_db_host_fails_fast():
    from sqlalchemy.ext.asyncio import create_async_engine
    bad_url = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@255.255.255.255:{settings.DB_PORT}/{settings.DB_NAME}"
    bad_engine = create_async_engine(bad_url, connect_args={"timeout": 1})
    
    with pytest.raises(Exception):
        async with bad_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    await bad_engine.dispose()

# PGVECTOR EXTENSION TESTS

@pytest.mark.asyncio
async def test_vector_extension_active(db_session: AsyncSession):
    # Test that `vector` extension is installed and active
    result = await db_session.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
    row = result.fetchone()
    assert row is not None

@pytest.mark.asyncio
async def test_agent_memories_embedding_dimension(db_session: AsyncSession):
    # Test that inserting a vector with wrong dimension (e.g., 3-D) raises an error
    memory = AgentMemory(
        persona_id="test_persona",
        content="test content",
        embedding=[0.1, 0.2, 0.3] # 3-D instead of 768-D
    )
    db_session.add(memory)
    with pytest.raises(Exception) as exc_info:
        await db_session.commit()
    
    # Postrgres pgvector error for dimension mismatch
    assert "768" in str(exc_info.value)
    await db_session.rollback()

    # Test it accepts exactly 768-dimension vectors
    memory2 = AgentMemory(
        persona_id="test_persona",
        content="test content",
        embedding=[0.1] * 768
    )
    db_session.add(memory2)
    await db_session.commit()
    # No error = passed

# TABLE INTEGRITY TESTS

@pytest.mark.asyncio
async def test_expected_tables_exist(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
    tables = [row[0] for row in result.fetchall()]
    assert "agent_memories" in tables
    assert "general_data" in tables

@pytest.mark.asyncio
async def test_agent_memories_columns(db_session: AsyncSession):
    result = await db_session.execute(text(
        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'agent_memories'"
    ))
    columns = {row[0]: row[1] for row in result.fetchall()}
    assert "id" in columns
    assert "uuid" in columns["id"].lower()
    
    assert "persona_id" in columns
    assert "content" in columns
    assert "embedding" in columns
    assert "USER-DEFINED" in columns["embedding"] # vector
    assert "created_at" in columns

@pytest.mark.asyncio
async def test_general_data_columns(db_session: AsyncSession):
    result = await db_session.execute(text(
        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'general_data'"
    ))
    columns = {row[0]: row[1] for row in result.fetchall()}
    assert "id" in columns
    assert "uuid" in columns["id"].lower()
    
    assert "title" in columns
    assert "description" in columns
    assert "payload" in columns
    assert "jsonb" in columns["payload"].lower()
    assert "created_at" in columns
    assert "updated_at" in columns

@pytest.mark.asyncio
async def test_indexes_exist(db_session: AsyncSession):
    result = await db_session.execute(text(
        "SELECT indexname FROM pg_indexes WHERE tablename IN ('agent_memories', 'general_data')"
    ))
    indexes = [row[0] for row in result.fetchall()]
    assert any("persona_id" in idx for idx in indexes)
    assert any("title" in idx for idx in indexes)

# DATA INTEGRITY TESTS

@pytest.mark.asyncio
async def test_insert_agent_memories(db_session: AsyncSession):
    memory = AgentMemory(persona_id="p1", content="c1", embedding=[0.1]*768)
    db_session.add(memory)
    await db_session.commit()
    
    # Retrieve
    retrieved = await db_session.get(AgentMemory, memory.id)
    assert retrieved is not None
    assert retrieved.persona_id == "p1"
    assert retrieved.created_at is not None

@pytest.mark.asyncio
async def test_insert_general_data(db_session: AsyncSession):
    data = GeneralData(title="t1", payload={"key": "value"})
    db_session.add(data)
    await db_session.commit()
    
    retrieved = await db_session.get(GeneralData, data.id)
    assert retrieved is not None
    assert retrieved.title == "t1"
    assert retrieved.payload == {"key": "value"}
    assert retrieved.created_at is not None
    assert retrieved.updated_at is not None

@pytest.mark.asyncio
async def test_general_data_updated_at_auto_updates(db_session: AsyncSession):
    data = GeneralData(title="t1", payload={})
    db_session.add(data)
    await db_session.commit()
    
    first_updated_at = data.updated_at
    
    # modify
    data.title = "t2"
    db_session.add(data)
    await db_session.commit()
    await db_session.refresh(data)
    
    assert data.updated_at > first_updated_at

@pytest.mark.asyncio
async def test_insert_agent_memories_without_content(db_session: AsyncSession):
    memory = AgentMemory(persona_id="p1", embedding=[0.1]*768)
    db_session.add(memory)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

@pytest.mark.asyncio
async def test_insert_duplicate_uuid(db_session: AsyncSession):
    memory1 = AgentMemory(persona_id="p1", content="c1", embedding=[0.1]*768)
    db_session.add(memory1)
    await db_session.commit()
    db_session.expunge(memory1)
    
    memory2 = AgentMemory(id=memory1.id, persona_id="p2", content="c2", embedding=[0.2]*768)
    db_session.add(memory2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

# TRANSACTION TESTS

@pytest.mark.asyncio
async def test_transaction_commit_and_rollback(db_session: AsyncSession):
    # Test commit
    data1 = GeneralData(title="commit_test")
    db_session.add(data1)
    await db_session.commit()
    
    retrieved = await db_session.get(GeneralData, data1.id)
    assert retrieved is not None
    
    # Test rollback
    data2 = GeneralData(title="rollback_test")
    db_session.add(data2)
    await db_session.rollback()
    
    # Verify it doesn't exist
    result = await db_session.execute(text(f"SELECT * FROM general_data WHERE title = 'rollback_test'"))
    assert result.fetchone() is None

@pytest.mark.asyncio
async def test_concurrent_writes():
    from tests.conftest import TestingSessionLocal
    
    async def insert_record(i):
        async with TestingSessionLocal() as session:
            data = GeneralData(title=f"concurrent_{i}")
            session.add(data)
            await session.commit()
            
    # Run 10 concurrently
    tasks = [insert_record(i) for i in range(10)]
    await asyncio.gather(*tasks)
    
    # Verify 10 records inserted
    async with TestingSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM general_data WHERE title LIKE 'concurrent_%'"))
        assert result.scalar() == 10

# CONNECTION POOL TESTS

@pytest.mark.asyncio
async def test_multiple_simultaneous_sessions():
    from tests.conftest import TestingSessionLocal
    
    async def open_session():
        async with TestingSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar()
            
    tasks = [open_session() for _ in range(20)]
    results = await asyncio.gather(*tasks)
    assert sum(results) == 20

@pytest.mark.asyncio
async def test_nullpool_is_used():
    from tests.conftest import test_engine
    from sqlalchemy.pool import NullPool
    # Test_engine must use NullPool to avoid pool limit errors in tests
    assert isinstance(test_engine.pool, NullPool)

@pytest.mark.asyncio
async def test_session_closed_on_exception():
    from tests.conftest import TestingSessionLocal
    
    try:
        async with TestingSessionLocal() as session:
            raise ValueError("Mid-transaction error")
    except ValueError:
        pass
    
    # The session context manager automatically rolls back and cleans up
    assert not session.in_transaction()
