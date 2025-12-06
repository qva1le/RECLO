from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.attributes import AttributesOrm
    from src.models.products import ProductsOrm


class ProductAttributesValuesOrm(Base):
    __tablename__ = "product_attributes_values"
    __table_args__ = (
        UniqueConstraint("product_id", "attribute_id", name="uq_product_attr_single"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True, nullable=False)
    attribute_id: Mapped[int] = mapped_column(ForeignKey("attributes.id"), index=True, nullable=False)

    value_string: Mapped[str | None] = mapped_column(String(50))
    value_int: Mapped[int | None] = mapped_column(Integer)
    value_float: Mapped[float | None] = mapped_column(Float)
    value_bool: Mapped[bool | None] = mapped_column(Boolean)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    product: Mapped["ProductsOrm"] = relationship(back_populates="attributes")
    attribute: Mapped["AttributesOrm"] = relationship(back_populates="values")
