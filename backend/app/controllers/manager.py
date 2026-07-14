from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.application import Application, ApplicationStatus
from app.models.user import RoleEnum, User
from app.schemas.application import (
    ApplicationPage,
    ApplicationRead,
    ManagerReviewComment,
)
from app.schemas.user import AdminUserCreate, UserPage, UserRead, UserRoleUpdate
from app.services.application_service import ApplicationService
from app.services.user_service import UserService

router = APIRouter(prefix="/manager/applications", tags=["manager"])
users_router = APIRouter(prefix="/manager/users", tags=["manager"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
ManagerUser = Annotated[User, Depends(require_role(RoleEnum.MANAGER, RoleEnum.ADMIN))]
AdminUser = Annotated[User, Depends(require_role(RoleEnum.ADMIN))]


@users_router.get(
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


@users_router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (admin only)",
)
async def create_user(data: AdminUserCreate, db: DbSession, _: AdminUser) -> User:
    return await UserService(db).create(data.email, data.password, data.role)


@users_router.patch(
    "/{user_id}/role",
    response_model=UserRead,
    summary="Change a user's role (admin only)",
)
async def update_user_role(
    user_id: int, data: UserRoleUpdate, db: DbSession, actor: AdminUser
) -> User:
    return await UserService(db).update_role(actor, user_id, data.role)


@users_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (admin only)",
)
async def delete_user(user_id: int, db: DbSession, actor: AdminUser) -> None:
    await UserService(db).delete(actor, user_id)


@router.get(
    "",
    response_model=ApplicationPage,
    summary="List all applications with pagination, filtering, and sorting",
)
async def list_applications(
    db: DbSession,
    _: ManagerUser,
    status: ApplicationStatus | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: Literal["created_at", "floor"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> ApplicationPage:
    items, total = await ApplicationService(db).list_all(
        status, page, size, sort_by, order == "desc"
    )
    return ApplicationPage(items=items, total=total, page=page, size=size)


@router.post(
    "/{application_id}/approve",
    response_model=ApplicationRead,
    summary="Approve a pending or needs-changes application",
)
async def approve_application(
    application_id: int, db: DbSession, _: ManagerUser
) -> Application:
    return await ApplicationService(db).approve(application_id)


@router.post(
    "/{application_id}/reject",
    response_model=ApplicationRead,
    summary="Reject a pending or needs-changes application",
)
async def reject_application(
    application_id: int, db: DbSession, _: ManagerUser
) -> Application:
    return await ApplicationService(db).reject(application_id)


@router.post(
    "/{application_id}/request-changes",
    response_model=ApplicationRead,
    summary="Send a pending application back for changes with a required comment",
)
async def request_changes(
    application_id: int, data: ManagerReviewComment, db: DbSession, _: ManagerUser
) -> Application:
    return await ApplicationService(db).request_changes(application_id, data.comment)


@router.post(
    "/{application_id}/revoke",
    response_model=ApplicationRead,
    summary="Revoke an approved application, reverting it back to pending review",
)
async def revoke_application(
    application_id: int, db: DbSession, _: ManagerUser
) -> Application:
    return await ApplicationService(db).revoke(application_id)
