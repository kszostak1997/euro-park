from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import RoleEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


class AdminUserCreate(UserCreate):
    role: RoleEnum = RoleEnum.USER


class UserRoleUpdate(BaseModel):
    role: RoleEnum


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime

    @field_validator("created_at", mode="after")
    @classmethod
    def _ensure_utc(cls, value: datetime) -> datetime:
        return value if value.tzinfo else value.replace(tzinfo=UTC)


class UserPage(BaseModel):
    items: list[UserRead]
    total: int
    page: int
    size: int
