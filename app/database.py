"""Infraestrutura de banco de dados assíncrona."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa para os modelos ORM."""


class DatabaseManager:
    """Gerencia engine, session maker e inicialização do banco."""

    def __init__(self, database_url: str) -> None:
        self.engine: AsyncEngine = create_async_engine(database_url, future=True)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def create_all(self) -> None:
        """Cria as tabelas no banco local."""

        from app.models.account_model import Account
        from app.models.transaction_model import Transaction
        from app.models.user_model import User

        _ = (User, Account, Transaction)
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        """Encerra conexões abertas pelo engine."""

        await self.engine.dispose()

    async def session(self) -> AsyncIterator[AsyncSession]:
        """Fornece uma sessão assíncrona."""

        async with self.session_factory() as session:
            yield session
