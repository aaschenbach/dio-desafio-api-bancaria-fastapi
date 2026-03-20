"""Ponto de entrada da aplicação FastAPI."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.database import DatabaseManager
from app.routers import accounts, auth, transactions


def create_app(settings: Settings | None = None) -> FastAPI:
    """Cria e configura a aplicação FastAPI."""

    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        db_manager = DatabaseManager(resolved_settings.database_url)
        app.state.db_manager = db_manager
        await db_manager.create_all()
        yield
        await db_manager.dispose()

    app = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.app_version,
        description=resolved_settings.app_description,
        lifespan=lifespan,
    )
    register_exception_handlers(app)
    app.include_router(auth.router)
    app.include_router(accounts.router)
    app.include_router(transactions.router)
    return app


app = create_app()
