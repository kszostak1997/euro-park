import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.application import ApplicationStatus

REGISTRATION_NUMBER_PATTERN = re.compile(r"^[A-Z]{2,3}[A-Z0-9]{4,5}$")


def _normalize_registration_number(value: str) -> str:
    normalized = value.strip().upper().replace(" ", "").replace("-", "")
    if not REGISTRATION_NUMBER_PATTERN.match(normalized):
        raise ValueError("Nieprawidłowy numer rejestracyjny")
    return normalized


class ApplicationCreate(BaseModel):
    registration_number: str = Field(min_length=4, max_length=20)
    floor: int
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("registration_number")
    @classmethod
    def validate_registration_number(cls, value: str) -> str:
        return _normalize_registration_number(value)


class ApplicationUpdate(BaseModel):
    registration_number: str | None = Field(default=None, min_length=4, max_length=20)
    floor: int | None = None
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("registration_number")
    @classmethod
    def validate_registration_number(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _normalize_registration_number(value)


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    registration_number: str
    floor: int
    status: ApplicationStatus
    comment: str | None
    created_at: datetime
