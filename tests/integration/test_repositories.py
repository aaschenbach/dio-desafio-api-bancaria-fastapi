"""Testes de integração dos repositórios com banco SQLite assíncrono."""

from decimal import Decimal

import pytest

from app.models.account_model import Account
from app.models.transaction_model import Transaction, TransactionType
from app.models.user_model import User
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_persist_account_and_find_by_user(app) -> None:
    async for session in app.state.db_manager.session():
        user_repository = UserRepository(session)
        account_repository = AccountRepository(session)

        user = User(
            username="repo_user",
            email="repo_user@example.com",
            hashed_password="hash",
            is_active=True,
        )
        await user_repository.create(user)
        await session.commit()

        account = Account(
            agency="0001",
            account_number="5555-1",
            owner_name="Repo User",
            owner_document=None,
            user_id=user.id,
        )
        await account_repository.create(account)
        await session.commit()

        accounts = await account_repository.list_by_user(user.id)
        assert len(accounts) == 1
        assert accounts[0].account_number == "5555-1"


@pytest.mark.asyncio
async def test_persist_transactions_and_summary(app) -> None:
    async for session in app.state.db_manager.session():
        user_repository = UserRepository(session)
        account_repository = AccountRepository(session)
        transaction_repository = TransactionRepository(session)

        user = User(
            username="repo_user2",
            email="repo_user2@example.com",
            hashed_password="hash",
            is_active=True,
        )
        await user_repository.create(user)
        await session.flush()

        account = Account(
            agency="0001",
            account_number="8888-1",
            owner_name="Repo User 2",
            owner_document=None,
            user_id=user.id,
        )
        await account_repository.create(account)
        await session.flush()

        await transaction_repository.create(
            Transaction(
                account_id=account.id,
                type=TransactionType.DEPOSIT,
                amount=Decimal("300.00"),
                description="Depósito",
            )
        )
        await transaction_repository.create(
            Transaction(
                account_id=account.id,
                type=TransactionType.WITHDRAWAL,
                amount=Decimal("40.00"),
                description="Saque",
            )
        )
        await session.commit()

        transactions = await transaction_repository.list_by_account(account.id)
        summary = await transaction_repository.get_summary(account.id)

        assert len(transactions) == 2
        assert summary.balance == Decimal("260.00")
        assert summary.total_deposits == Decimal("300.00")
        assert summary.total_withdrawals == Decimal("40.00")
        assert summary.total_transactions == 2
