from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 -- registers models on Base.metadata
from app.core.database import Base, get_db
from app.core.rate_limit import limiter
from app.main import app
from app.models.user import RoleEnum, User

limiter.enabled = False

DEFAULT_TEST_PASSWORD = "supersecret123"

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def register_and_login(
    client: AsyncClient, email: str, password: str = DEFAULT_TEST_PASSWORD
) -> str:
    await client.post("/auth/register", json={"email": email, "password": password})
    login = await client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    return login.json()["access_token"]


async def promote_to_manager(db_session: AsyncSession, email: str) -> None:
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.role = RoleEnum.MANAGER
    db_session.add(user)
    await db_session.commit()
