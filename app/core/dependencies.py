"""Dependências reutilizáveis do FastAPI."""

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.database import DatabaseManager
from app.models.user_model import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_database_manager(request: Request) -> DatabaseManager:
    """Recupera o gerenciador de banco armazenado no estado da aplicação."""

    return request.app.state.db_manager


async def get_session(
    db_manager: DatabaseManager = Depends(get_database_manager),
) -> AsyncIterator[AsyncSession]:
    """Fornece sessão assíncrona para os handlers."""

    async for session in db_manager.session():
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> User:
    """Resolve o usuário autenticado a partir do JWT."""

    subject = decode_access_token(token, settings)
    user_repository = UserRepository(session)
    user = await user_repository.get_by_id(int(subject))
    if user is None or not user.is_active:
        raise AuthenticationError("Usuário autenticado não encontrado ou inativo.")
    return user
