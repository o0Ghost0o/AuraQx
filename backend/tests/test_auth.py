import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.config import settings


@pytest.mark.asyncio
async def test_login_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={"username": settings.auth_username, "password": settings.auth_password}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 15 * 60


@pytest.mark.asyncio
async def test_login_invalid_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={"username": settings.auth_username, "password": "wrongpassword"}
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login
        login_resp = await client.post(
            "/api/auth/login",
            json={"username": settings.auth_username, "password": settings.auth_password}
        )
        data = login_resp.json()
        ref_token = data["refresh_token"]

        # 2. Refresh
        refresh_resp = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": ref_token}
        )
        assert refresh_resp.status_code == 200
        new_data = refresh_resp.json()
        assert "access_token" in new_data
        assert new_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/auth/me")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login
        login_resp = await client.post(
            "/api/auth/login",
            json={"username": settings.auth_username, "password": settings.auth_password}
        )
        token = login_resp.json()["access_token"]

        # Access /api/auth/me
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        user = response.json()
        assert user["username"] == settings.auth_username
