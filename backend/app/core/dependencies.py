from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import (
    InactiveUserError,
    InsufficientRoleError,
    InvalidTokenError,
)
from app.core.security import decode_token
from app.models.user import RoleEnum, User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    if credentials is None:
        raise InvalidTokenError("Missing bearer token")

    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise InvalidTokenError

    user = await UserRepository(db).get_by_id(int(payload["sub"]))
    if user is None:
        raise InvalidTokenError
    if not user.is_active:
        raise InactiveUserError
    return user


def require_role(*roles: RoleEnum):
    async def dependency(
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if user.role not in roles:
            raise InsufficientRoleError
        return user

    return dependency


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
ManagerUser = Annotated[User, Depends(require_role(RoleEnum.MANAGER, RoleEnum.ADMIN))]
AdminUser = Annotated[User, Depends(require_role(RoleEnum.ADMIN))]
