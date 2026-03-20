"""Fixtures compartilhadas da suíte de testes."""

from collections.abc import AsyncIterator
from pathlib import Path
import sys

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def test_settings(tmp_path) -> Settings:
    """Configurações isoladas para testes."""

    database_file = tmp_path / "test.db"
    return Settings(
        app_name="API Bancária Teste",
        app_version="test",
        app_description="Aplicação de teste",
        database_url=f"sqlite+aiosqlite:///{database_file.as_posix()}",
        jwt_secret_key="segredo-de-teste",
        access_token_expire_minutes=30,
    )


@pytest_asyncio.fixture
async def app(test_settings: Settings):
    """Instância da aplicação configurada para testes."""

    application = create_app(test_settings)
    async with LifespanManager(application):
        yield application


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    """Cliente HTTP assíncrono para testes de API."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Cria um usuário padrão para testes."""

    payload = {
        "username": "cliente1",
        "email": "cliente1@example.com",
        "password": "Senha123",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    return payload


@pytest_asyncio.fixture
async def auth_token(client: AsyncClient, registered_user: dict) -> str:
    """Obtém token JWT para o usuário de teste."""

    response = await client.post(
        "/auth/login",
        json={
            "username_or_email": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token: str) -> dict[str, str]:
    """Headers autenticados para chamadas protegidas."""

    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def created_account(client: AsyncClient, auth_headers: dict[str, str]) -> dict:
    """Cria uma conta corrente para os testes."""

    response = await client.post(
        "/accounts",
        json={
            "agency": "0001",
            "account_number": "12345-6",
            "owner_name": "Cliente Teste",
            "owner_document": "123.456.789-00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()
