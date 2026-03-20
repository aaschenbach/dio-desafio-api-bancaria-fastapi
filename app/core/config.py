"""Configurações centralizadas da aplicação."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Representa as configurações de ambiente da aplicação."""

    app_name: str = Field(default="API Bancária FastAPI")
    app_version: str = Field(default="0.1.0")
    app_description: str = Field(
        default="API RESTful assíncrona para contas correntes e transações bancárias."
    )
    database_url: str = Field(default="sqlite+aiosqlite:///./bank.db")
    jwt_secret_key: str = Field(default="troque-esta-chave-em-producao")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instância cacheada das configurações."""

    return Settings()
