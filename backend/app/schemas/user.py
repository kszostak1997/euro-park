from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import RoleEnum
from app.schemas.validators import AwareDatetime


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
    created_at: AwareDatetime


class UserPage(BaseModel):
    items: list[UserRead]
    total: int
    page: int
    size: int
