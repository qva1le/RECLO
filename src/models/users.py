from __future__ import annotations


from datetime import datetime

from sqlalchemy import String, DateTime, UniqueConstraint, func, Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.schemas.enums import UserStatus
from src.database import Base


class UsersOrm(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    status:Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus, name="userstatus"),
        default=UserStatus.pending_email,
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(30), default="user", nullable=False)
    subscription_expires_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
    )

    product_reviews: Mapped[list["ProductReviewsOrm"]] = relationship(
        "ProductReviewsOrm",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    product_fires: Mapped[list["ProductFiresOrm"]] = relationship(
        "ProductFiresOrm",
        back_populates="user",
        cascade="all, delete-orphan"
    )

