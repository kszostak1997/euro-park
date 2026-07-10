from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.applications import router as applications_router
from app.controllers.auth import router as auth_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

configure_logging(debug=settings.debug)

app = FastAPI(
    title=settings.app_name,
    description="System wniosków o miejsce parkingowe",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(applications_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
