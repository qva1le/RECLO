from datetime import datetime
from time import timezone

from sqlalchemy import String, DateTime, UniqueConstraint, func, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
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
        Enum(UserStatus),
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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
    )
