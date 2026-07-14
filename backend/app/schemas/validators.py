import re
from typing import Annotated

from pydantic import AfterValidator, Field

REGISTRATION_NUMBER_PATTERN = re.compile(r"^[A-Z]{2,3}[A-Z0-9]{4,5}$")


def normalize_registration_number(value: str) -> str:
    normalized = value.strip().upper().replace(" ", "").replace("-", "")
    if not REGISTRATION_NUMBER_PATTERN.match(normalized):
        raise ValueError("Nieprawidłowy numer rejestracyjny")
    return normalized


RegistrationNumber = Annotated[
    str,
    Field(min_length=4, max_length=20),
    AfterValidator(normalize_registration_number),
]
