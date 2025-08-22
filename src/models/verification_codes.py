from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Enum, String, DateTime, Integer, Boolean, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.users import UsersOrm
from src.schemas.enums import CodeStatus


class VerificationCodesOrm(Base):
    __tablename__ = "verification_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[CodeStatus] = mapped_column(
        Enum(CodeStatus, name="codestatus"),
        nullable=False
    )
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user: Mapped["UsersOrm"] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "type", "code_hash", name="uq_verification_codes_user_type_hash"),
    )
