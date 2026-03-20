"""Schemas do contexto de contas correntes."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import SchemaBase
from app.schemas.transaction import TransactionListItem


class AccountCreate(BaseModel):
    """Payload para criação de conta."""

    agency: str = Field(min_length=1, max_length=10, examples=["0001"])
    account_number: str = Field(min_length=1, max_length=20, examples=["12345-6"])
    owner_name: str = Field(min_length=3, max_length=120, examples=["João da Silva"])
    owner_document: str | None = Field(default=None, max_length=30, examples=["123.456.789-00"])


class AccountResponse(SchemaBase):
    """Resposta pública de conta corrente."""

    id: int
    agency: str
    account_number: str
    owner_name: str
    owner_document: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime


class AccountListResponse(BaseModel):
    """Lista de contas do usuário autenticado."""

    items: list[AccountResponse]


class StatementResponse(BaseModel):
    """Resposta consolidada do extrato bancário."""

    account: AccountResponse
    transactions: list[TransactionListItem]
    current_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    total_transactions: int
