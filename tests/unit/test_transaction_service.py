"""Testes unitários do serviço de transações."""

from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.exceptions import ValidationDomainError
from app.services.transaction_service import TransactionService


class AsyncAccountServiceStub:
    async def get_account(self, account_id: int, user):
        return SimpleNamespace(id=account_id)


class AsyncTransactionRepositoryStub:
    async def get_summary(self, account_id: int):
        return SimpleNamespace(balance=Decimal("5.00"))


def test_calculate_balance() -> None:
    result = TransactionService.calculate_balance(
        total_deposits=Decimal("200.00"),
        total_withdrawals=Decimal("80.00"),
        total_transactions=3,
    )

    assert result.current_balance == Decimal("120.00")
    assert result.total_transactions == 3


def test_validate_invalid_amount() -> None:
    with pytest.raises(ValidationDomainError):
        TransactionService._validate_positive_amount(Decimal("0.00"), "depósito")


@pytest.mark.asyncio
async def test_validate_withdrawal_insufficient_balance() -> None:
    session = SimpleNamespace(commit=None)
    service = TransactionService(session)  # type: ignore[arg-type]
    service.account_service = AsyncAccountServiceStub()
    service.transaction_repository = AsyncTransactionRepositoryStub()

    with pytest.raises(ValidationDomainError):
        await service.create_withdrawal(
            account_id=1,
            amount=Decimal("10.00"),
            description=None,
            user=SimpleNamespace(id=1),
        )
