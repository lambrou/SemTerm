import pytest


@pytest.mark.anyio
async def test_read_main(test_client):
    response = await test_client.get("/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_health_check(test_client):
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
