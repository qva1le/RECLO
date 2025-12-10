from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.products import ProductsOrm
    from src.models.users import UsersOrm


class ProductFiresOrm(Base):
    __tablename__ = "product_fires"
    __table_args__ = (
        # Один пользователь — один огонёк на товар
        UniqueConstraint("product_id", "user_id", name="uq_fire_product_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    product = relationship(
        "ProductsOrm",
        back_populates="fires",
    )
    user = relationship(
        "UsersOrm",
        back_populates="product_fires",
    )
