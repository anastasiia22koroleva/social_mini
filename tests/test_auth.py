import pytest
from httpx import AsyncClient
from social_mini.main import app


@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "secret123",
            "first_name": "Test",
            "last_name": "User"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_user():
    # Сначала зарегистрируем пользователя
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "secret123",
            "first_name": "Login",
            "last_name": "User"
        })

        # Попробуем войти
        response = await ac.post("/auth/token", data={
            "username": "loginuser",
            "password": "secret123"
        })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"