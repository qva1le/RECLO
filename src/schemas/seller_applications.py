from pydantic import BaseModel, Field, ConfigDict

from src.schemas.enums import BusinessType, ShopType


class SellerApplicationCreate(BaseModel):
    fio: str = Field(..., max_length=100)
    phone_number: str = Field(..., max_length=100)
    inn: str = Field(..., min_length=10, max_length=12)

    business_type: BusinessType

    shop_name: str = Field(..., max_length=40)
    avatar_url: str | None = Field(..., max_length=500)
    description: str | None = Field(..., max_length=500)
    city: str = Field(..., max_length=60)
    shop_type: ShopType
    social_links: str | None = Field(...)


class SellerApplicationOut(BaseModel):
    id: int
    fio: str
    phone_number: str
    inn: str
    business_type: BusinessType
    shop_name: str
    avatar_url: str | None
    description: str | None
    city: str
    shop_type: ShopType
    social_links: str | None

    model_config = ConfigDict(from_attributes=True)

class SellerApplicationsReview(BaseModel):
    approve: bool
    rejection_reason: str | None = None

