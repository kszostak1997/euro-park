from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.application import Application
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate, db: DbSession, current_user: CurrentUser
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
async def update_application(
    application_id: int,
    data: ApplicationUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Application:
    return await ApplicationService(db).update(current_user, application_id, data)
