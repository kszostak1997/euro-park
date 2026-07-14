from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.seed import SEED_USERS, seed_admin_user
from app.models.user import User


async def test_seed_admin_user_creates_all_seed_users(db_session: AsyncSession) -> None:
    await seed_admin_user(db_session)

    for email, _password, role in SEED_USERS:
        result = await db_session.execute(select(User).where(User.email == email))
        user = result.scalar_one()
        assert user.role == role


async def test_seed_admin_user_is_idempotent(db_session: AsyncSession) -> None:
    await seed_admin_user(db_session)
    await seed_admin_user(db_session)

    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == len(SEED_USERS)
