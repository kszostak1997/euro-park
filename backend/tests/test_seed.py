from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.seed import seed_admin_user
from app.models.user import RoleEnum, User


async def test_seed_admin_user_creates_admin(db_session: AsyncSession) -> None:
    await seed_admin_user(db_session)

    result = await db_session.execute(
        select(User).where(User.email == settings.admin_email)
    )
    admin = result.scalar_one()
    assert admin.role == RoleEnum.ADMIN


async def test_seed_admin_user_is_idempotent(db_session: AsyncSession) -> None:
    await seed_admin_user(db_session)
    await seed_admin_user(db_session)

    result = await db_session.execute(
        select(User).where(User.email == settings.admin_email)
    )
    admins = result.scalars().all()
    assert len(admins) == 1
