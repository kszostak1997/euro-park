import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class ApplicationStatus(enum.StrEnum):
    PENDING = "PENDING"
    NEEDS_CHANGES = "NEEDS_CHANGES"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    registration_number: Mapped[str] = mapped_column(String(20))
    floor: Mapped[int] = mapped_column(Integer)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, native_enum=False, length=20),
        default=ApplicationStatus.PENDING,
    )
    comment: Mapped[str | None] = mapped_column(String(500), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="applications")
