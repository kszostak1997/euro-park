from pydantic import BaseModel, Field, field_validator

from app.schemas.validators import normalize_registration_number


class BarrierCheckRequest(BaseModel):
    registration_number: str = Field(min_length=4, max_length=20)

    @field_validator("registration_number")
    @classmethod
    def validate_registration_number(cls, value: str) -> str:
        return normalize_registration_number(value)


class BarrierCheckResponse(BaseModel):
    registration_number: str
    access_granted: bool
