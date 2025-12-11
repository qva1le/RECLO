from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database import Base
from src.models.product_reviews import ProductReviewsOrm
from src.models.product_fires import ProductFiresOrm
from src.models.product_attribute_values import ProductAttributesValuesOrm


class ProductsOrm(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        ForeignKey("shops.id"),
        index=True,
        nullable=False,
    )
    article: Mapped[str] = mapped_column(
        String(16),
        unique=True,
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    fires_count:   Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating_avg:    Mapped[float | None] = mapped_column(Float)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    reviews = relationship(
        ProductReviewsOrm,
        back_populates="product",
        cascade="all, delete-orphan",
    )

    fires = relationship(
        ProductFiresOrm,
        back_populates="product",
        cascade="all, delete-orphan",
    )

    attributes = relationship(
        ProductAttributesValuesOrm,
        back_populates="product",
        cascade="all, delete-orphan",
    )
