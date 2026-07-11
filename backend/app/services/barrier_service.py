import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.application_repository import ApplicationRepository

logger = logging.getLogger("app.services.barrier")


class BarrierService:
    def __init__(self, db: AsyncSession) -> None:
        self.applications = ApplicationRepository(db)

    async def check_access(self, registration_number: str) -> bool:
        application = await self.applications.get_approved_by_plate(registration_number)
        granted = application is not None
        logger.info(
            "Barrier check for %s: %s",
            registration_number,
            "granted" if granted else "denied",
        )
        return granted
