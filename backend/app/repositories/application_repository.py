from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import paginate
from app.models.application import Application, ApplicationStatus

SORTABLE_COLUMNS = {
    "created_at": Application.created_at,
    "floor": Application.floor,
}


class ApplicationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        user_id: int,
        registration_number: str,
        floor: int,
        applicant_comment: str | None,
    ) -> Application:
        application = Application(
            user_id=user_id,
            registration_number=registration_number,
            floor=floor,
            applicant_comment=applicant_comment,
        )
        self.db.add(application)
        await self.db.flush()
        await self.db.refresh(application)
        return application

    async def get_by_id(self, application_id: int) -> Application | None:
        result = await self.db.execute(
            select(Application)
            .options(selectinload(Application.user))
            .where(Application.id == application_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[Application]:
        result = await self.db.execute(
            select(Application)
            .options(selectinload(Application.user))
            .where(Application.user_id == user_id)
            .order_by(Application.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_all(
        self,
        status_filter: ApplicationStatus | None,
        offset: int,
        limit: int,
        sort_by: str,
        descending: bool,
    ) -> tuple[list[Application], int]:
        filters = [Application.status == status_filter] if status_filter else []
        column = SORTABLE_COLUMNS[sort_by]
        order = column.desc() if descending else column.asc()
        stmt = (
            select(Application)
            .options(selectinload(Application.user))
            .where(*filters)
            .order_by(order)
        )
        return await paginate(self.db, stmt, offset, limit)

    async def get_approved_by_plate(
        self, registration_number: str
    ) -> Application | None:
        result = await self.db.execute(
            select(Application)
            .where(
                Application.registration_number == registration_number,
                Application.status == ApplicationStatus.APPROVED,
            )
            .limit(1)
        )
        return result.scalar_one_or_none()
