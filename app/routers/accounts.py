"""Rotas do contexto de contas correntes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_session
from app.models.user_model import User
from app.schemas.account import AccountCreate, AccountListResponse, AccountResponse, StatementResponse
from app.schemas.common import APIErrorResponse
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar conta corrente",
    description="Cria uma conta corrente vinculada ao usuário autenticado.",
    responses={401: {"model": APIErrorResponse}, 409: {"model": APIErrorResponse}},
)
async def create_account(
    payload: AccountCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> AccountResponse:
    """Cria uma conta corrente."""

    service = AccountService(session)
    account = await service.create_account(payload, current_user)
    return AccountResponse.model_validate(account)


@router.get(
    "",
    response_model=AccountListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar contas",
    description="Lista as contas pertencentes ao usuário autenticado.",
    responses={401: {"model": APIErrorResponse}},
)
async def list_accounts(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> AccountListResponse:
    """Lista contas do usuário autenticado."""

    service = AccountService(session)
    accounts = await service.list_accounts(current_user)
    return AccountListResponse(items=[AccountResponse.model_validate(item) for item in accounts])


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Detalhar conta",
    description="Retorna os dados de uma conta corrente do usuário autenticado.",
    responses={
        401: {"model": APIErrorResponse},
        403: {"model": APIErrorResponse},
        404: {"model": APIErrorResponse},
    },
)
async def get_account(
    account_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> AccountResponse:
    """Busca conta por identificador."""

    service = AccountService(session)
    account = await service.get_account(account_id, current_user)
    return AccountResponse.model_validate(account)


@router.get(
    "/{account_id}/statement",
    response_model=StatementResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar extrato",
    description="Exibe extrato completo da conta, incluindo saldo e totais.",
    responses={
        401: {"model": APIErrorResponse},
        403: {"model": APIErrorResponse},
        404: {"model": APIErrorResponse},
    },
)
async def get_statement(
    account_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> StatementResponse:
    """Retorna extrato completo da conta."""

    service = TransactionService(session)
    return await service.get_statement(account_id, current_user)
