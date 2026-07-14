from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator

from app.models.application import ApplicationStatus
from app.schemas.validators import RegistrationNumber

# Matches the floors offered by the frontend's application form (Piętro 0-2).
MIN_FLOOR = 0
MAX_FLOOR = 2


def _strip(value: str) -> str:
    return value.strip()


class ApplicationCreate(BaseModel):
    registration_number: RegistrationNumber
    floor: int = Field(ge=MIN_FLOOR, le=MAX_FLOOR)
    applicant_comment: str | None = Field(default=None, max_length=500)


class ApplicationUpdate(BaseModel):
    registration_number: RegistrationNumber | None = None
    floor: int | None = Field(default=None, ge=MIN_FLOOR, le=MAX_FLOOR)
    applicant_comment: str | None = Field(default=None, max_length=500)


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_email: str
    registration_number: str
    floor: int
    status: ApplicationStatus
    applicant_comment: str | None
    manager_comment: str | None
    created_at: datetime

    @field_validator("created_at", mode="after")
    @classmethod
    def _ensure_utc(cls, value: datetime) -> datetime:
        # SQLite (local dev default) stores naive timestamps while Postgres
        # (docker) returns tz-aware ones; normalize both to UTC so the
        # frontend always parses an unambiguous instant.
        return value if value.tzinfo else value.replace(tzinfo=UTC)


class ApplicationPage(BaseModel):
    items: list[ApplicationRead]
    total: int
    page: int
    size: int


class ManagerReviewComment(BaseModel):
    comment: Annotated[
        str, BeforeValidator(_strip), Field(min_length=1, max_length=500)
    ]
