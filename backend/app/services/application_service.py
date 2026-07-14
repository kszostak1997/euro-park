import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ApplicationNotEditableError,
    ApplicationNotFoundError,
    InvalidStatusTransitionError,
)
from app.models.application import Application, ApplicationStatus
from app.models.user import User
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import ApplicationCreate, ApplicationUpdate

logger = logging.getLogger("app.services.application")

EDITABLE_STATUSES = {ApplicationStatus.PENDING, ApplicationStatus.NEEDS_CHANGES}
REVIEWABLE_STATUSES = {ApplicationStatus.PENDING, ApplicationStatus.NEEDS_CHANGES}
REVOCABLE_STATUSES = {ApplicationStatus.APPROVED}


class ApplicationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.applications = ApplicationRepository(db)

    async def _reload(self, application: Application) -> Application:
        await self.db.refresh(application)
        await self.db.refresh(application, attribute_names=["user"])
        return application

    async def create(self, user: User, data: ApplicationCreate) -> Application:
        application = await self.applications.create(
            user.id, data.registration_number, data.floor, data.applicant_comment
        )
        application.user = user
        await self.db.commit()
        logger.info("Created application id=%s for user id=%s", application.id, user.id)
        return application

    async def list_own(self, user: User) -> list[Application]:
        return await self.applications.list_by_user(user.id)

    async def get_own(self, user: User, application_id: int) -> Application:
        application = await self.applications.get_by_id(application_id)
        if application is None or application.user_id != user.id:
            raise ApplicationNotFoundError
        return application

    async def update(
        self, user: User, application_id: int, data: ApplicationUpdate
    ) -> Application:
        application = await self.get_own(user, application_id)
        if application.status not in EDITABLE_STATUSES:
            raise ApplicationNotEditableError

        changed = False
        if (
            data.registration_number is not None
            and data.registration_number != application.registration_number
        ):
            application.registration_number = data.registration_number
            changed = True
        if data.floor is not None and data.floor != application.floor:
            application.floor = data.floor
            changed = True
        if (
            data.applicant_comment is not None
            and data.applicant_comment != application.applicant_comment
        ):
            application.applicant_comment = data.applicant_comment
            changed = True

        if changed and application.status == ApplicationStatus.NEEDS_CHANGES:
            application.status = ApplicationStatus.PENDING

        self.db.add(application)
        await self.db.commit()
        await self._reload(application)
        logger.info("Updated application id=%s", application.id)
        return application

    async def list_all(
        self,
        status_filter: ApplicationStatus | None,
        page: int,
        size: int,
        sort_by: str,
        descending: bool,
    ) -> tuple[list[Application], int]:
        offset = (page - 1) * size
        return await self.applications.list_all(
            status_filter, offset, size, sort_by, descending
        )

    async def _get_reviewable(self, application_id: int) -> Application:
        application = await self.applications.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError
        if application.status not in REVIEWABLE_STATUSES:
            raise InvalidStatusTransitionError
        return application

    async def approve(self, application_id: int) -> Application:
        application = await self._get_reviewable(application_id)
        application.status = ApplicationStatus.APPROVED
        self.db.add(application)
        await self.db.commit()
        await self._reload(application)
        logger.info("Approved application id=%s", application.id)
        return application

    async def reject(self, application_id: int) -> Application:
        application = await self._get_reviewable(application_id)
        application.status = ApplicationStatus.REJECTED
        self.db.add(application)
        await self.db.commit()
        await self._reload(application)
        logger.info("Rejected application id=%s", application.id)
        return application

    async def request_changes(self, application_id: int, comment: str) -> Application:
        application = await self._get_reviewable(application_id)
        application.status = ApplicationStatus.NEEDS_CHANGES
        application.manager_comment = comment
        self.db.add(application)
        await self.db.commit()
        await self._reload(application)
        logger.info("Requested changes for application id=%s", application.id)
        return application

    async def revoke(self, application_id: int) -> Application:
        application = await self.applications.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError
        if application.status not in REVOCABLE_STATUSES:
            raise InvalidStatusTransitionError
        application.status = ApplicationStatus.PENDING
        self.db.add(application)
        await self.db.commit()
        await self._reload(application)
        logger.info("Revoked approval for application id=%s", application.id)
        return application
