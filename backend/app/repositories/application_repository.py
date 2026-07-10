from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application


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
