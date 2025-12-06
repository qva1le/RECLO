from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.products import ProductsOrm
    from src.models.users import UsersOrm


class ProductReviewsOrm(Base):
    __tablename__ = "product_reviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    product: Mapped["ProductsOrm"] = relationship(back_populates="reviews")
    user: Mapped["UsersOrm"] = relationship(back_populates="product_reviews")


