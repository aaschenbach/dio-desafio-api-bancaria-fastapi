"""Repository para operações de usuário."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User


class UserRepository:
    """Encapsula o acesso a dados de usuários."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        """Persiste um usuário."""

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Busca um usuário por identificador."""

        return await self.session.get(User, user_id)

    async def get_by_username(self, username: str) -> User | None:
        """Busca um usuário por username."""

        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Busca um usuário por email."""

        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_login(self, username_or_email: str) -> User | None:
        """Busca um usuário por username ou email."""

        result = await self.session.execute(
            select(User).where(
                or_(User.username == username_or_email, User.email == username_or_email)
            )
        )
        return result.scalar_one_or_none()
