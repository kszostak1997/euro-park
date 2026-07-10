import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.time import utcnow
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenPair
from app.schemas.user import UserCreate

logger = logging.getLogger("app.services.auth")


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    async def register(self, data: UserCreate) -> User:
        email = data.email.lower()
        if await self.users.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError

        user = await self.users.create(email, hash_password(data.password))
        await self.db.commit()
        logger.info("Registered new user id=%s", user.id)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.users.get_by_email(email.lower())
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError
        if not user.is_active:
            raise InvalidCredentialsError
        return user

    async def issue_tokens(self, user: User) -> TokenPair:
        access_token = create_access_token(user.id, user.role)
        refresh_token, jti, expires_at = create_refresh_token(user.id)
        await self.refresh_tokens.create(user.id, jti, expires_at)
        await self.db.commit()
        logger.info("Issued token pair for user id=%s", user.id)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self.authenticate(email, password)
        return await self.issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidTokenError

        record = await self.refresh_tokens.get_by_jti(payload["jti"])
        if record is None:
            raise InvalidTokenError

        if record.revoked_at is not None or record.expires_at <= utcnow():
            raise InvalidTokenError

        await self.refresh_tokens.revoke(record)
        user = await self.users.get_by_id(record.user_id)
        if user is None or not user.is_active:
            await self.db.commit()
            raise InvalidTokenError

        return await self.issue_tokens(user)
