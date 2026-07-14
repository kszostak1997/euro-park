import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CannotModifyOwnAccountError,
    EmailAlreadyRegisteredError,
    UserNotFoundError,
)
from app.core.security import hash_password
from app.models.user import RoleEnum, User
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("app.services.user")


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def list_all(self, page: int, size: int) -> tuple[list[User], int]:
        offset = (page - 1) * size
        return await self.users.list_all(offset, size)

    async def create(self, email: str, password: str, role: RoleEnum) -> User:
        normalized_email = email.lower()
        if await self.users.get_by_email(normalized_email) is not None:
            raise EmailAlreadyRegisteredError

        user = await self.users.create(normalized_email, hash_password(password))
        user.role = role
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info("Admin-created user id=%s with role=%s", user.id, role)
        return user

    async def _get_modifiable(self, actor: User, user_id: int) -> User:
        if actor.id == user_id:
            raise CannotModifyOwnAccountError
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError
        return user

    async def update_role(self, actor: User, user_id: int, role: RoleEnum) -> User:
        user = await self._get_modifiable(actor, user_id)

        user.role = role
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info("Changed role of user id=%s to %s", user.id, role)
        return user

    async def delete(self, actor: User, user_id: int) -> None:
        user = await self._get_modifiable(actor, user_id)

        await self.db.delete(user)
        await self.db.commit()
        logger.info("Deleted user id=%s", user_id)
