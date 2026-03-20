"""Repository para operações de contas correntes."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account_model import Account


class AccountRepository:
    """Encapsula a persistência de contas correntes."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, account: Account) -> Account:
        """Persiste uma conta."""

        self.session.add(account)
        await self.session.flush()
        await self.session.refresh(account)
        return account

    async def get_by_id(self, account_id: int) -> Account | None:
        """Busca conta por id."""

        return await self.session.get(Account, account_id)

    async def get_by_agency_and_number(self, agency: str, account_number: str) -> Account | None:
        """Busca conta por agência e número."""

        result = await self.session.execute(
            select(Account).where(
                Account.agency == agency,
                Account.account_number == account_number,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[Account]:
        """Lista contas de um usuário."""

        result = await self.session.execute(
            select(Account).where(Account.user_id == user_id).order_by(Account.created_at.asc())
        )
        return list(result.scalars().all())
