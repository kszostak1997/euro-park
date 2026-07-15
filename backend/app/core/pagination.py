from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select


def page_to_offset(page: int, size: int) -> int:
    return (page - 1) * size


async def paginate[T](
    db: AsyncSession, stmt: Select[tuple[T]], offset: int, limit: int
) -> tuple[list[T], int]:
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    result = await db.execute(stmt.offset(offset).limit(limit))
    return list(result.scalars().all()), total
