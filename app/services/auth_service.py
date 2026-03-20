"""Serviços de autenticação e registro de usuários."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AuthenticationError, ConflictError, ValidationDomainError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserCreate


class AuthService:
    """Orquestra registro e autenticação de usuários."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.user_repository = UserRepository(session)

    async def register_user(self, payload: UserCreate) -> User:
        """Registra um novo usuário validando unicidade."""

        if await self.user_repository.get_by_username(payload.username):
            raise ConflictError("O username informado já está em uso.")
        if await self.user_repository.get_by_email(payload.email):
            raise ConflictError("O email informado já está em uso.")

        user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            is_active=True,
        )
        await self.user_repository.create(user)
        await self.session.commit()
        return user

    async def authenticate(self, username_or_email: str, password: str) -> TokenResponse:
        """Autentica um usuário e emite token JWT."""

        user = await self.user_repository.get_by_login(username_or_email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Credenciais inválidas.")
        if not user.is_active:
            raise ValidationDomainError("Usuário inativo não pode autenticar.")

        token = create_access_token(subject=str(user.id), settings=self.settings)
        return TokenResponse(access_token=token)
