from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.application import ApplicationStatus
from app.schemas.validators import normalize_registration_number


class ApplicationCreate(BaseModel):
    registration_number: str = Field(min_length=4, max_length=20)
    floor: int
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("registration_number")
    @classmethod
    def validate_registration_number(cls, value: str) -> str:
        return normalize_registration_number(value)


class ApplicationUpdate(BaseModel):
    registration_number: str | None = Field(default=None, min_length=4, max_length=20)
    floor: int | None = None
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("registration_number")
    @classmethod
    def validate_registration_number(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return normalize_registration_number(value)


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    registration_number: str
    floor: int
    status: ApplicationStatus
    comment: str | None
    created_at: datetime


class ApplicationPage(BaseModel):
    items: list[ApplicationRead]
    total: int
    page: int
    size: int


class ManagerReviewComment(BaseModel):
    comment: str = Field(min_length=1, max_length=500)
