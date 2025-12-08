import pytest
from httpx import AsyncClient
from social_mini.main import app


@pytest.mark.asyncio
async def test_create_post():
    # Сначала получим токен
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Регистрация
        await ac.post("/auth/register", json={
            "username": "postuser",
            "email": "post@example.com",
            "password": "secret123",
            "first_name": "Post",
            "last_name": "User"
        })

        # Вход
        token_resp = await ac.post("/auth/token", data={
            "username": "postuser",
            "password": "secret123"
        })
        token = token_resp.json()["access_token"]

        # Создание поста
        response = await ac.post("/posts/", json={
            "title": "Test Post",
            "content": "This is a test post."
        }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"


@pytest.mark.asyncio
async def test_get_posts():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/posts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)