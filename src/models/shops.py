from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Enum as SAEnum
from src.database import Base
from src.schemas.enums import BusinessType, ShopType, ShopStatus


class ShopsOrm(Base):
    __tablename__ = "shops"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("seller_applications.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(60), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), nullable=False)
    business_type: Mapped[BusinessType] = mapped_column(
        SAEnum(BusinessType),
        nullable=False,
    )
    shop_type: Mapped[ShopType] = mapped_column(
        SAEnum(ShopType),
        nullable=False,
    )

    instagram_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vk_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telegram_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tiktok_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[ShopStatus] = mapped_column(
        SAEnum(ShopStatus),
        default=ShopStatus.active,
        nullable=False,
        index=True,
    )
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
