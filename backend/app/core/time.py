from datetime import UTC, datetime


def utcnow() -> datetime:
    """Current UTC time as a naive datetime (matches the plain DateTime() columns)."""
    return datetime.now(UTC).replace(tzinfo=None)
