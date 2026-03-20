"""Testes unitários do serviço de contas."""

from types import SimpleNamespace

import pytest

from app.core.exceptions import ConflictError
from app.schemas.account import AccountCreate
from app.services.account_service import AccountService


class FakeAccountRepository:
    def __init__(self, existing=None) -> None:
        self.existing = existing
        self.created = None

    async def get_by_agency_and_number(self, agency: str, account_number: str):
        return self.existing

    async def create(self, account):
        account.id = 1
        self.created = account
        return account


class FakeSession:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True


@pytest.mark.asyncio
async def test_create_account_success() -> None:
    session = FakeSession()
    service = AccountService(session)  # type: ignore[arg-type]
    service.account_repository = FakeAccountRepository()
    user = SimpleNamespace(id=1)

    account = await service.create_account(
        AccountCreate(
            agency="0001",
            account_number="12345-6",
            owner_name="Cliente Teste",
            owner_document=None,
        ),
        user,
    )

    assert account.id == 1
    assert session.committed is True


@pytest.mark.asyncio
async def test_create_account_conflict() -> None:
    session = FakeSession()
    service = AccountService(session)  # type: ignore[arg-type]
    service.account_repository = FakeAccountRepository(existing=object())
    user = SimpleNamespace(id=1)

    with pytest.raises(ConflictError):
        await service.create_account(
            AccountCreate(
                agency="0001",
                account_number="12345-6",
                owner_name="Cliente Teste",
                owner_document=None,
            ),
            user,
        )
