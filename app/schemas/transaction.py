"""Schemas do contexto de transações."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.transaction_model import TransactionType
from app.schemas.common import SchemaBase


class TransactionCreateDeposit(BaseModel):
    """Payload para criação de depósito."""

    account_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, decimal_places=2, max_digits=12, examples=[150.50])
    description: str | None = Field(default=None, max_length=255)


class TransactionCreateWithdraw(BaseModel):
    """Payload para criação de saque."""

    account_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, decimal_places=2, max_digits=12, examples=[50.00])
    description: str | None = Field(default=None, max_length=255)


class TransactionListItem(SchemaBase):
    """Item de transação exibido em extrato."""

    id: int
    account_id: int
    type: TransactionType
    amount: Decimal
    description: str | None
    created_at: datetime


class TransactionResponse(TransactionListItem):
    """Resposta detalhada da transação criada."""


class BalanceResponse(BaseModel):
    """Resposta da operação financeira com saldo atualizado."""

    transaction: TransactionResponse
    balance: Decimal
