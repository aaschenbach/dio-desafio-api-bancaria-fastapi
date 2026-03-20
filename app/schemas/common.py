"""Schemas comuns e reutilizáveis."""

from pydantic import BaseModel, ConfigDict


class APIErrorDetail(BaseModel):
    """Detalhe padronizado de erro da API."""

    code: str
    message: str


class APIErrorResponse(BaseModel):
    """Envelope padronizado para erros de domínio."""

    detail: APIErrorDetail


class SchemaBase(BaseModel):
    """Base para schemas com suporte a atributos ORM."""

    model_config = ConfigDict(from_attributes=True)
