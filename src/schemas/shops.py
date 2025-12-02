from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.enums import BusinessType, ShopType, ShopStatus


class ShopEditUser(BaseModel):
    name: str
    avatar_url: str
    description: str
    city: str
    instagram_url: str | None = None
    vk_url: str | None = None
    telegram_url: str | None = None
    tiktok_url: str | None = None

class ShopEditAdmin(BaseModel):
    owner_id: int
    application_id: int
    name: str
    avatar_url: str
    description: str
    city: str
    inn: str
    business_type: BusinessType
    shop_type: ShopType
    status: ShopStatus

class ShopOut(BaseModel):
    id: int
    owner_id: int
    application_id: int
    name: str
    avatar_url: str | None
    description: str | None
    city: str
    inn: str
    business_type: BusinessType
    shop_type: ShopType
    instagram_url: str | None = None
    vk_url: str | None = None
    telegram_url: str | None = None
    tiktok_url: str | None = None
    status: ShopStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShopUpdateUser(BaseModel):
    name: str | None = Field(None, max_length=40)
    avatar_url: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=60)

    instagram_url: str | None = None
    vk_url: str | None = None
    telegram_url: str | None = None
    tiktok_url: str | None = None


class ShopUpdateAdmin(BaseModel):
    name: str | None = Field(None, max_length=40)
    avatar_url: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=60)
    inn: str | None = Field(None, min_length=10, max_length=12)
    business_type: BusinessType | None = None
    shop_type: ShopType | None = None

class ShopStatusChange(BaseModel):
    status: ShopStatus

class ShopsPublic(BaseModel):
    name: str
    avatar_url: str
    description: str
    shop_type: str
    city: str

    instagram_url: str | None = None
    vk_url: str | None = None
    telegram_url: str | None = None
    tiktok_url: str | None = None
