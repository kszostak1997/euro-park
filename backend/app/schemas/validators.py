import re

REGISTRATION_NUMBER_PATTERN = re.compile(r"^[A-Z]{2,3}[A-Z0-9]{4,5}$")


def normalize_registration_number(value: str) -> str:
    normalized = value.strip().upper().replace(" ", "").replace("-", "")
    if not REGISTRATION_NUMBER_PATTERN.match(normalized):
        raise ValueError("Nieprawidłowy numer rejestracyjny")
    return normalized
