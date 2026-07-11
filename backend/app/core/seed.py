import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import RoleEnum
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("app.core.seed")


async def seed_admin_user(db: AsyncSession) -> None:
    users = UserRepository(db)
    if await users.get_by_email(settings.admin_email) is not None:
        return

    admin = await users.create(
        settings.admin_email, hash_password(settings.admin_password)
    )
    admin.role = RoleEnum.ADMIN
    db.add(admin)
    await db.commit()
    logger.info("Seeded default admin user id=%s", admin.id)
