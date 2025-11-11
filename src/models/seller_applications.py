from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column


from src.database import Base
from src.schemas.enums import SellerApplicationsStatus, BusinessType, ShopType


class SellerApplicationsOrm(Base):
    __tablename__ = "seller_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    fio: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(20))
    inn: Mapped[str] = mapped_column(String(12))

    business_type: Mapped[BusinessType] = mapped_column(
        SAEnum(BusinessType),
        nullable=False
    )

    shop_name: Mapped[str] = mapped_column(String(40))
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(60))
    shop_type: Mapped[ShopType] = mapped_column(
        SAEnum(ShopType),
        nullable=False
    )
    social_links: Mapped[str] = mapped_column(Text, nullable=True)

    status: Mapped[SellerApplicationsStatus] = mapped_column(
        SAEnum(SellerApplicationsStatus),
        default=SellerApplicationsStatus.pending,
        nullable=False,
        index=True,
    )
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)





