from fastapi import APIRouter, Request, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.rate_limit import limiter
from app.models.application import Application
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_application(
    request: Request,
    data: ApplicationCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Application:
    return await ApplicationService(db).create(current_user, data)


@router.get("", response_model=list[ApplicationRead])
async def list_applications(
    db: DbSession, current_user: CurrentUser
) -> list[Application]:
    return await ApplicationService(db).list_own(current_user)


@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: int, db: DbSession, current_user: CurrentUser
) -> Application:
    return await ApplicationService(db).get_own(current_user, application_id)


@router.patch("/{application_id}", response_model=ApplicationRead)
@limiter.limit("20/minute")
async def update_application(
    request: Request,
    application_id: int,
    data: ApplicationUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Application:
    return await ApplicationService(db).update(current_user, application_id, data)
