"""Rotas do contexto de transações bancárias."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_session
from app.models.user_model import User
from app.schemas.common import APIErrorResponse
from app.schemas.transaction import (
    BalanceResponse,
    TransactionCreateDeposit,
    TransactionCreateWithdraw,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "/deposit",
    response_model=BalanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar depósito",
    description="Registra um depósito em uma conta do usuário autenticado.",
    responses={
        400: {"model": APIErrorResponse},
        401: {"model": APIErrorResponse},
        403: {"model": APIErrorResponse},
        404: {"model": APIErrorResponse},
    },
)
async def create_deposit(
    payload: TransactionCreateDeposit,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BalanceResponse:
    """Registra um depósito."""

    service = TransactionService(session)
    return await service.create_deposit(
        account_id=payload.account_id,
        amount=payload.amount,
        description=payload.description,
        user=current_user,
    )


@router.post(
    "/withdraw",
    response_model=BalanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar saque",
    description="Registra um saque validando saldo suficiente.",
    responses={
        400: {"model": APIErrorResponse},
        401: {"model": APIErrorResponse},
        403: {"model": APIErrorResponse},
        404: {"model": APIErrorResponse},
    },
)
async def create_withdraw(
    payload: TransactionCreateWithdraw,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BalanceResponse:
    """Registra um saque."""

    service = TransactionService(session)
    return await service.create_withdrawal(
        account_id=payload.account_id,
        amount=payload.amount,
        description=payload.description,
        user=current_user,
    )
