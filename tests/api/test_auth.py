"""Testes de API do contexto de autenticação."""

from httpx import AsyncClient


async def test_register_user(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={
            "username": "joao",
            "email": "joao@example.com",
            "password": "Senha123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "joao"
    assert data["email"] == "joao@example.com"


async def test_login_user(client: AsyncClient, registered_user: dict) -> None:
    response = await client.post(
        "/auth/login",
        json={
            "username_or_email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
