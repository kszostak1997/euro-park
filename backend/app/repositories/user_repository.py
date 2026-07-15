from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import paginate
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def list_all(self, offset: int, limit: int) -> tuple[list[User], int]:
        stmt = select(User).order_by(User.created_at.desc())
        return await paginate(self.db, stmt, offset, limit)
