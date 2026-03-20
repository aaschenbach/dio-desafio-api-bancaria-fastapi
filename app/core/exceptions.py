"""Exceções de domínio e mapeamento padronizado de erros."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Exceção base para erros de domínio."""

    status_code: int = 400
    code: str = "domain_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class AuthenticationError(DomainError):
    """Erro para autenticação inválida."""

    status_code = 401
    code = "authentication_error"


class AuthorizationError(DomainError):
    """Erro para acesso negado."""

    status_code = 403
    code = "authorization_error"


class ResourceNotFoundError(DomainError):
    """Erro para recurso inexistente."""

    status_code = 404
    code = "resource_not_found"


class ConflictError(DomainError):
    """Erro para conflitos de unicidade ou estado."""

    status_code = 409
    code = "conflict_error"


class ValidationDomainError(DomainError):
    """Erro para regras de validação de negócio."""

    status_code = 400
    code = "validation_error"


async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    """Traduz exceções de domínio para resposta HTTP JSON padronizada."""

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": {"code": exc.code, "message": exc.message}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra handlers globais da aplicação."""

    app.add_exception_handler(DomainError, domain_error_handler)
