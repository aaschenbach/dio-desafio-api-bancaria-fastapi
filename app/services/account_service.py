"""Serviços do contexto de contas correntes."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, ConflictError, ResourceNotFoundError
from app.models.account_model import Account
from app.models.user_model import User
from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate


class AccountService:
    """Orquestra operações de contas correntes."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.account_repository = AccountRepository(session)

    async def create_account(self, payload: AccountCreate, user: User) -> Account:
        """Cria uma conta para o usuário autenticado."""

        existing = await self.account_repository.get_by_agency_and_number(
            payload.agency,
            payload.account_number,
        )
        if existing is not None:
            raise ConflictError("Já existe uma conta com a mesma agência e número.")

        account = Account(
            agency=payload.agency,
            account_number=payload.account_number,
            owner_name=payload.owner_name,
            owner_document=payload.owner_document,
            user_id=user.id,
        )
        await self.account_repository.create(account)
        await self.session.commit()
        return account

    async def list_accounts(self, user: User) -> list[Account]:
        """Lista as contas do usuário autenticado."""

        return await self.account_repository.list_by_user(user.id)

    async def get_account(self, account_id: int, user: User) -> Account:
        """Busca uma conta validando propriedade."""

        account = await self.account_repository.get_by_id(account_id)
        if account is None:
            raise ResourceNotFoundError("Conta corrente não encontrada.")
        if account.user_id != user.id:
            raise AuthorizationError("Você não pode acessar uma conta de outro usuário.")
        return account
