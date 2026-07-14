from typing import Literal

from fastapi import APIRouter, Query, Request

from app.core.dependencies import DbSession, ManagerUser
from app.core.rate_limit import limiter
from app.models.application import Application, ApplicationStatus
from app.schemas.application import (
    ApplicationPage,
    ApplicationRead,
    ManagerReviewComment,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/manager/applications", tags=["manager"])


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
@limiter.limit("60/minute")
async def approve_application(
    request: Request, application_id: int, db: DbSession, _: ManagerUser
) -> Application:
    return await ApplicationService(db).approve(application_id)


@router.post(
    "/{application_id}/reject",
    response_model=ApplicationRead,
    summary="Reject a pending or needs-changes application",
)
@limiter.limit("60/minute")
async def reject_application(
    request: Request, application_id: int, db: DbSession, _: ManagerUser
) -> Application:
    return await ApplicationService(db).reject(application_id)


@router.post(
    "/{application_id}/request-changes",
    response_model=ApplicationRead,
    summary="Send a pending application back for changes with a required comment",
)
@limiter.limit("60/minute")
async def request_changes(
    request: Request,
    application_id: int,
    data: ManagerReviewComment,
    db: DbSession,
    _: ManagerUser,
) -> Application:
    return await ApplicationService(db).request_changes(application_id, data.comment)


@router.post(
    "/{application_id}/revoke",
    response_model=ApplicationRead,
    summary="Revoke an approved application, reverting it back to pending review",
)
@limiter.limit("60/minute")
async def revoke_application(
    request: Request, application_id: int, db: DbSession, _: ManagerUser
) -> Application:
    return await ApplicationService(db).revoke(application_id)
