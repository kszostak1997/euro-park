import uuid
from datetime import datetime, timedelta
from typing import Any, Literal

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import InvalidTokenError
from app.core.time import utcnow
from app.models.user import RoleEnum

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def _create_token(
    subject: int,
    token_type: Literal["access", "refresh"],
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    now = utcnow()
    expires_at = now + expires_delta
    jti = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": expires_at,
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti, expires_at


def create_access_token(user_id: int, role: RoleEnum) -> str:
    token, _, _ = _create_token(
        user_id,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims={"role": role.value},
    )
    return token


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    return _create_token(
        user_id, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError from exc
