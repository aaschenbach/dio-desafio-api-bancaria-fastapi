"""Funções de segurança, hash de senha e JWT."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.core.config import Settings
from app.core.exceptions import AuthenticationError

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Gera hash seguro para uma senha."""

    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Valida uma senha em relação ao hash armazenado."""

    return password_hash.verify(password, hashed_password)


def create_access_token(
    subject: str,
    settings: Settings,
    expires_delta: timedelta | None = None,
) -> str:
    """Gera um JWT assinado para autenticação."""

    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> str:
    """Decodifica um token JWT e devolve o subject."""

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise AuthenticationError("Token de acesso inválido ou expirado.") from exc

    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError("Token de acesso inválido.")

    return str(subject)
