from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Integer, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.schemas.enums import AttributeDataType

if TYPE_CHECKING:
    from src.models.product_attribute_values import ProductAttributesValuesOrm


class AttributesOrm(Base):
    __tablename__ = "attributes"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    data_type: Mapped[AttributeDataType] = mapped_column(
        SAEnum(AttributeDataType, name="attribute_data_type"),
        default=AttributeDataType.STRING,
        nullable=False,
    )

    # см, кг и т.п.
    unit: Mapped[str | None] = mapped_column(String(20))

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


    values = relationship(
        "ProductAttributesValuesOrm",
        back_populates="attribute",
        cascade="all, delete-orphan",
    )
