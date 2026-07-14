from pydantic import BaseModel

from app.schemas.validators import RegistrationNumber


class BarrierCheckRequest(BaseModel):
    registration_number: RegistrationNumber


class BarrierCheckResponse(BaseModel):
    registration_number: str
    access_granted: bool
