"""Testes unitários do serviço de autenticação."""

from types import SimpleNamespace

import pytest

from app.core.config import Settings
from app.core.exceptions import AuthenticationError
from app.core.security import hash_password
from app.services.auth_service import AuthService


class FakeUserRepository:
    def __init__(self, user=None) -> None:
        self.user = user

    async def get_by_login(self, username_or_email: str):
        return self.user

    async def get_by_username(self, username: str):
        return None

    async def get_by_email(self, email: str):
        return None


class FakeSession:
    async def commit(self) -> None:
        return None


@pytest.mark.asyncio
async def test_authenticate_success() -> None:
    settings = Settings(jwt_secret_key="teste", database_url="sqlite+aiosqlite:///./fake.db")
    user = SimpleNamespace(
        id=1,
        hashed_password=hash_password("Senha123"),
        is_active=True,
    )
    service = AuthService(FakeSession(), settings)  # type: ignore[arg-type]
    service.user_repository = FakeUserRepository(user)

    result = await service.authenticate("user", "Senha123")

    assert result.token_type == "bearer"
    assert isinstance(result.access_token, str)


@pytest.mark.asyncio
async def test_authenticate_invalid_credentials() -> None:
    settings = Settings(jwt_secret_key="teste", database_url="sqlite+aiosqlite:///./fake.db")
    service = AuthService(FakeSession(), settings)  # type: ignore[arg-type]
    service.user_repository = FakeUserRepository(user=None)

    with pytest.raises(AuthenticationError):
        await service.authenticate("user", "Senha123")
