"""Repository para transações bancárias."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction_model import Transaction, TransactionType


@dataclass(slots=True)
class TransactionSummary:
    """Resumo financeiro consolidado de uma conta."""

    balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    total_transactions: int


class TransactionRepository:
    """Encapsula a persistência de transações."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, transaction: Transaction) -> Transaction:
        """Persiste uma transação."""

        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)
        return transaction

    async def list_by_account(self, account_id: int) -> list[Transaction]:
        """Lista transações de uma conta em ordem cronológica."""

        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.created_at.asc(), Transaction.id.asc())
        )
        return list(result.scalars().all())

    async def get_summary(self, account_id: int) -> TransactionSummary:
        """Calcula saldo e totais agregados da conta."""

        deposits_expr = func.coalesce(
            func.sum(Transaction.amount).filter(Transaction.type == TransactionType.DEPOSIT),
            0,
        )
        withdrawals_expr = func.coalesce(
            func.sum(Transaction.amount).filter(Transaction.type == TransactionType.WITHDRAWAL),
            0,
        )
        count_expr = func.count(Transaction.id)

        result = await self.session.execute(
            select(deposits_expr, withdrawals_expr, count_expr).where(
                Transaction.account_id == account_id
            )
        )
        total_deposits, total_withdrawals, total_transactions = result.one()
        deposits = Decimal(total_deposits)
        withdrawals = Decimal(total_withdrawals)
        return TransactionSummary(
            balance=deposits - withdrawals,
            total_deposits=deposits,
            total_withdrawals=withdrawals,
            total_transactions=int(total_transactions or 0),
        )
