"""Rotas do contexto de autenticação."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.dependencies import get_session
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserResponse
from app.schemas.common import APIErrorResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuário",
    description="Cria um novo usuário para autenticação na API bancária.",
    responses={409: {"model": APIErrorResponse}},
)
async def register(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> UserResponse:
    """Cria um novo usuário."""

    service = AuthService(session, settings)
    user = await service.register_user(payload)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticar usuário",
    description="Autentica por username ou email e devolve um JWT Bearer.",
    responses={401: {"model": APIErrorResponse}},
)
async def login(
    payload: UserLogin,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """Autentica e devolve token de acesso."""

    service = AuthService(session, settings)
    return await service.authenticate(payload.username_or_email, payload.password)
