"""Serviços de movimentação bancária e extrato."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationDomainError
from app.models.transaction_model import Transaction, TransactionType
from app.models.user_model import User
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.account import StatementResponse
from app.schemas.transaction import BalanceResponse
from app.services.account_service import AccountService


@dataclass(slots=True)
class BalanceComputation:
    """Representa o saldo calculado a partir de totais."""

    current_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    total_transactions: int


class TransactionService:
    """Orquestra depósitos, saques e extratos."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.account_service = AccountService(session)
        self.transaction_repository = TransactionRepository(session)

    @staticmethod
    def calculate_balance(
        total_deposits: Decimal,
        total_withdrawals: Decimal,
        total_transactions: int,
    ) -> BalanceComputation:
        """Calcula saldo consolidado da conta."""

        return BalanceComputation(
            current_balance=total_deposits - total_withdrawals,
            total_deposits=total_deposits,
            total_withdrawals=total_withdrawals,
            total_transactions=total_transactions,
        )

    async def create_deposit(
        self,
        account_id: int,
        amount: Decimal,
        description: str | None,
        user: User,
    ) -> BalanceResponse:
        """Registra um depósito e retorna o saldo atualizado."""

        self._validate_positive_amount(amount, "depósito")
        account = await self.account_service.get_account(account_id, user)
        transaction = Transaction(
            account_id=account.id,
            type=TransactionType.DEPOSIT,
            amount=amount,
            description=description,
        )
        await self.transaction_repository.create(transaction)
        await self.session.commit()
        summary = await self.transaction_repository.get_summary(account.id)
        return BalanceResponse(transaction=transaction, balance=summary.balance)

    async def create_withdrawal(
        self,
        account_id: int,
        amount: Decimal,
        description: str | None,
        user: User,
    ) -> BalanceResponse:
        """Registra um saque validando saldo suficiente."""

        self._validate_positive_amount(amount, "saque")
        account = await self.account_service.get_account(account_id, user)
        summary = await self.transaction_repository.get_summary(account.id)
        if summary.balance < amount:
            raise ValidationDomainError("Saldo insuficiente para realizar o saque.")

        transaction = Transaction(
            account_id=account.id,
            type=TransactionType.WITHDRAWAL,
            amount=amount,
            description=description,
        )
        await self.transaction_repository.create(transaction)
        await self.session.commit()
        updated_summary = await self.transaction_repository.get_summary(account.id)
        return BalanceResponse(transaction=transaction, balance=updated_summary.balance)

    async def get_statement(self, account_id: int, user: User) -> StatementResponse:
        """Retorna o extrato consolidado da conta."""

        account = await self.account_service.get_account(account_id, user)
        transactions = await self.transaction_repository.list_by_account(account.id)
        summary = await self.transaction_repository.get_summary(account.id)
        computed = self.calculate_balance(
            total_deposits=summary.total_deposits,
            total_withdrawals=summary.total_withdrawals,
            total_transactions=summary.total_transactions,
        )
        return StatementResponse(
            account=account,
            transactions=transactions,
            current_balance=computed.current_balance,
            total_deposits=computed.total_deposits,
            total_withdrawals=computed.total_withdrawals,
            total_transactions=computed.total_transactions,
        )

    @staticmethod
    def _validate_positive_amount(amount: Decimal, operation: str) -> None:
        """Garante que o valor informado seja positivo."""

        if amount <= 0:
            raise ValidationDomainError(
                f"O valor informado para {operation} deve ser maior que zero."
            )
