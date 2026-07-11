from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.application import ApplicationStatus
from app.models.user import RoleEnum, User
from app.repositories.user_repository import UserRepository
from app.schemas.application import (
    ApplicationPage,
    ApplicationRead,
    ManagerReviewComment,
)
from app.schemas.user import UserRead
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/manager/applications", tags=["manager"])
users_router = APIRouter(prefix="/manager/users", tags=["manager"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
ManagerUser = Annotated[User, Depends(require_role(RoleEnum.MANAGER, RoleEnum.ADMIN))]


@users_router.get(
    "",
    response_model=list[UserRead],
    summary="List all registered users",
)
async def list_users(db: DbSession, _: ManagerUser) -> list[User]:
    return await UserRepository(db).list_all()


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
async def approve_application(application_id: int, db: DbSession, _: ManagerUser):
    return await ApplicationService(db).approve(application_id)


@router.post(
    "/{application_id}/reject",
    response_model=ApplicationRead,
    summary="Reject a pending or needs-changes application",
)
async def reject_application(application_id: int, db: DbSession, _: ManagerUser):
    return await ApplicationService(db).reject(application_id)


@router.post(
    "/{application_id}/request-changes",
    response_model=ApplicationRead,
    summary="Send a pending application back for changes with a required comment",
)
async def request_changes(
    application_id: int, data: ManagerReviewComment, db: DbSession, _: ManagerUser
):
    return await ApplicationService(db).request_changes(application_id, data.comment)
