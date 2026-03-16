import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.asyncio
async def test_ingest_memory_success(async_client: AsyncClient, auth_headers: dict, dummy_embedding: list):
    payload = {
        "persona_id": "test_persona",
        "content": "A system test memory.",
        "embedding": dummy_embedding
    }
    response = await async_client.post("/api/v1/memories/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["persona_id"] == "test_persona"
    assert data["content"] == "A system test memory."
    assert "id" in data

@pytest.mark.asyncio
async def test_ingest_memory_unauthorized(async_client: AsyncClient, dummy_embedding: list):
    payload = {
        "persona_id": "test_persona",
        "content": "A system test memory.",
        "embedding": dummy_embedding
    }
    response = await async_client.post("/api/v1/memories/", json=payload)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_ingest_memory_invalid_dimension(async_client: AsyncClient, auth_headers: dict):
    # Only 3 dimensions instead of 768
    payload = {
        "persona_id": "test_persona",
        "content": "Fast memory",
        "embedding": [0.1, 0.2, 0.3]
    }
    response = await async_client.post("/api/v1/memories/", json=payload, headers=auth_headers)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_ingest_memory_missing_fields(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "persona_id": "test_persona"
        # missing content and embedding
    }
    response = await async_client.post("/api/v1/memories/", json=payload, headers=auth_headers)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_search_memory_success(async_client: AsyncClient, seed_memory, dummy_embedding: list):
    payload = {
        "query_embedding": dummy_embedding,
        "persona_id": "persona_alpha",
        "limit": 5
    }
    response = await async_client.post("/api/v1/memories/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["persona_id"] == "persona_alpha"
    assert "distance" in data[0]

@pytest.mark.asyncio
async def test_search_memory_empty_result(async_client: AsyncClient, seed_memory, dummy_embedding: list):
    # Search for a persona that doesn't have records
    payload = {
        "query_embedding": dummy_embedding,
        "persona_id": "unknown_persona",
        "limit": 5
    }
    response = await async_client.post("/api/v1/memories/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data == []  # Not 404, just empty list

@pytest.mark.asyncio
async def test_search_memory_invalid_dimension(async_client: AsyncClient):
    payload = {
        "query_embedding": [0.1, 0.2] # Invalid length
    }
    response = await async_client.post("/api/v1/memories/search", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_search_memory_missing_embedding(async_client: AsyncClient):
    payload = {
        "persona_id": "test_persona",
    }
    response = await async_client.post("/api/v1/memories/search", json=payload)
    assert response.status_code == 422
