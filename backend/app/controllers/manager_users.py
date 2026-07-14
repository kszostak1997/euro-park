from fastapi import APIRouter, Query, Request, status

from app.core.dependencies import AdminUser, DbSession, ManagerUser
from app.core.rate_limit import limiter
from app.models.user import User
from app.schemas.user import AdminUserCreate, UserPage, UserRead, UserRoleUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/manager/users", tags=["manager"])


@router.get(
    "",
    response_model=UserPage,
    summary="List all registered users with pagination",
)
async def list_users(
    db: DbSession,
    _: ManagerUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> UserPage:
    items, total = await UserService(db).list_all(page, size)
    return UserPage(items=items, total=total, page=page, size=size)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (admin only)",
)
@limiter.limit("30/minute")
async def create_user(
    request: Request, data: AdminUserCreate, db: DbSession, _: AdminUser
) -> User:
    return await UserService(db).create(data.email, data.password, data.role)


@router.patch(
    "/{user_id}/role",
    response_model=UserRead,
    summary="Change a user's role (admin only)",
)
@limiter.limit("30/minute")
async def update_user_role(
    request: Request,
    user_id: int,
    data: UserRoleUpdate,
    db: DbSession,
    actor: AdminUser,
) -> User:
    return await UserService(db).update_role(actor, user_id, data.role)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (admin only)",
)
@limiter.limit("30/minute")
async def delete_user(
    request: Request, user_id: int, db: DbSession, actor: AdminUser
) -> None:
    await UserService(db).delete(actor, user_id)
