import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_create_data_success(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "title": "New Record",
        "description": "Description details",
        "payload": {"status": "active"}
    }
    response = await async_client.post("/api/v1/data/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Record"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_data_unauthorized(async_client: AsyncClient):
    payload = {"title": "New Record"}
    response = await async_client.post("/api/v1/data/", json=payload)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_data_empty_title(async_client: AsyncClient, auth_headers: dict):
    payload = {"description": "Missing title"}
    response = await async_client.post("/api/v1/data/", json=payload, headers=auth_headers)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_all_data(async_client: AsyncClient, seed_data):
    response = await async_client.get("/api/v1/data/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "Sample Title"

@pytest.mark.asyncio
async def test_get_all_data_pagination(async_client: AsyncClient, auth_headers: dict):
    # Insert multiple
    for i in range(10):
        await async_client.post("/api/v1/data/", json={"title": f"Item {i}"}, headers=auth_headers)
    
    response = await async_client.get("/api/v1/data/?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

@pytest.mark.asyncio
async def test_get_all_data_empty_db(async_client: AsyncClient):
    # Setup testing tables clears DB beforehand, but another test might have run payload.
    # To truly test empty DB, we can manually check an empty offset
    response = await async_client.get("/api/v1/data/?skip=9999&limit=5")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_data_by_id_success(async_client: AsyncClient, seed_data):
    response = await async_client.get(f"/api/v1/data/{seed_data.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(seed_data.id)

@pytest.mark.asyncio
async def test_get_data_by_id_not_found(async_client: AsyncClient):
    random_id = str(uuid.uuid4())
    response = await async_client.get(f"/api/v1/data/{random_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_data_by_id_invalid_format(async_client: AsyncClient):
    response = await async_client.get("/api/v1/data/not-a-uuid")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_data_success(async_client: AsyncClient, seed_data, auth_headers: dict):
    payload = {"title": "Updated Title"}
    response = await async_client.put(f"/api/v1/data/{seed_data.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

@pytest.mark.asyncio
async def test_update_data_unauthorized(async_client: AsyncClient, seed_data):
    payload = {"title": "Updated Title"}
    response = await async_client.put(f"/api/v1/data/{seed_data.id}", json=payload)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_data_not_found(async_client: AsyncClient, auth_headers: dict):
    random_id = str(uuid.uuid4())
    payload = {"title": "Updated Title"}
    response = await async_client.put(f"/api/v1/data/{random_id}", json=payload, headers=auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_data_success(async_client: AsyncClient, seed_data, auth_headers: dict):
    response = await async_client.delete(f"/api/v1/data/{seed_data.id}", headers=auth_headers)
    assert response.status_code in [200, 204]

@pytest.mark.asyncio
async def test_delete_data_unauthorized(async_client: AsyncClient, seed_data):
    response = await async_client.delete(f"/api/v1/data/{seed_data.id}")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_data_not_found(async_client: AsyncClient, auth_headers: dict):
    random_id = str(uuid.uuid4())
    response = await async_client.delete(f"/api/v1/data/{random_id}", headers=auth_headers)
    assert response.status_code == 404
