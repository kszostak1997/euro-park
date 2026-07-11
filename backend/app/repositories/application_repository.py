from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationStatus

SORTABLE_COLUMNS = {
    "created_at": Application.created_at,
    "floor": Application.floor,
}


class ApplicationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self, user_id: int, registration_number: str, floor: int, comment: str | None
    ) -> Application:
        application = Application(
            user_id=user_id,
            registration_number=registration_number,
            floor=floor,
            comment=comment,
        )
        self.db.add(application)
        await self.db.flush()
        await self.db.refresh(application)
        return application

    async def get_by_id(self, application_id: int) -> Application | None:
        return await self.db.get(Application, application_id)

    async def list_by_user(self, user_id: int) -> list[Application]:
        result = await self.db.execute(
            select(Application)
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

        count_stmt = select(func.count()).select_from(Application).where(*filters)
        total = (await self.db.execute(count_stmt)).scalar_one()

        column = SORTABLE_COLUMNS[sort_by]
        order = column.desc() if descending else column.asc()
        items_stmt = (
            select(Application)
            .where(*filters)
            .order_by(order)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(items_stmt)
        return list(result.scalars().all()), total

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
