"""Schemas do contexto de autenticação."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.common import SchemaBase


class UserCreate(BaseModel):
    """Payload de registro de usuário."""

    username: str = Field(min_length=3, max_length=50, examples=["joaosilva"])
    email: EmailStr = Field(examples=["joao@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["Senha123!"])

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Aplica validações mínimas de senha."""

        has_letter = any(char.isalpha() for char in value)
        has_number = any(char.isdigit() for char in value)
        if not has_letter or not has_number:
            raise ValueError("A senha deve conter letras e números.")
        return value


class UserLogin(BaseModel):
    """Payload de autenticação."""

    username_or_email: str = Field(
        min_length=3,
        max_length=255,
        examples=["joaosilva", "joao@example.com"],
    )
    password: str = Field(min_length=8, max_length=128)


class UserResponse(SchemaBase):
    """Resposta pública de usuário."""

    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Resposta de token JWT."""

    access_token: str
    token_type: str = "bearer"
