from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.controllers.applications import router as applications_router
from app.controllers.auth import router as auth_router
from app.controllers.barrier import router as barrier_router
from app.controllers.manager_applications import router as manager_applications_router
from app.controllers.manager_users import router as manager_users_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.core.seed import seed_admin_user
from app.middleware.logging import RequestLoggingMiddleware

configure_logging(debug=settings.debug)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    async with AsyncSessionLocal() as session:
        await seed_admin_user(session)
    yield


OPENAPI_TAGS = [
    {"name": "system", "description": "Health checks and service metadata."},
    {"name": "auth", "description": "Registration, login, and token refresh."},
    {
        "name": "applications",
        "description": "Resident-facing management of own parking applications.",
    },
    {
        "name": "manager",
        "description": "Manager/admin review workflow: list, approve, reject, "
        "request changes.",
    },
    {
        "name": "barrier",
        "description": "Barrier/gate integration for checking parking access.",
    },
]

app = FastAPI(
    title=settings.app_name,
    summary="System wniosków o miejsce parkingowe",
    description=(
        "API do zarządzania wnioskami o miejsce parkingowe: rejestracja "
        "mieszkańców, składanie i edycja wniosków, przegląd wniosków przez "
        "zarządcę oraz kontrola dostępu szlabanu."
    ),
    version="0.1.0",
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(applications_router)
app.include_router(manager_applications_router)
app.include_router(manager_users_router)
app.include_router(barrier_router)


@app.get("/health", tags=["system"], summary="Liveness check")
async def health() -> dict[str, str]:
    return {"status": "ok"}
