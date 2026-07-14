from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.application import ApplicationStatus
from app.schemas.validators import RegistrationNumber


class ApplicationCreate(BaseModel):
    registration_number: RegistrationNumber
    floor: int
    comment: str | None = Field(default=None, max_length=500)


class ApplicationUpdate(BaseModel):
    registration_number: RegistrationNumber | None = None
    floor: int | None = None
    comment: str | None = Field(default=None, max_length=500)


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
