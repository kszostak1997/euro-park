import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import RoleEnum
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("app.core.seed")

SEED_USERS: tuple[tuple[str, str, RoleEnum], ...] = (
    ("admin@admin.com", "admin", RoleEnum.ADMIN),
    ("manager@manager.com", "manager", RoleEnum.MANAGER),
    ("test@test.com", "test", RoleEnum.USER),
)


async def seed_admin_user(db: AsyncSession) -> None:
    users = UserRepository(db)

    for email, password, role in SEED_USERS:
        if await users.get_by_email(email) is not None:
            continue

        user = await users.create(email, hash_password(password))
        user.role = role
        db.add(user)
        logger.info("Seeded default %s user id=%s", role.value, user.id)

    await db.commit()
