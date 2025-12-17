from pydantic import BaseModel, constr, Field, conint, ConfigDict

from src.schemas.enums import AttributeDataType


class ProductBase(BaseModel):
    title: constr(max_length=100)
    description: str = Field(..., max_length=500)
    price: conint(ge=0)
    quantity: conint(ge=0) = 1


class ProductAttributeValueIn(BaseModel):
    attribute_id: int

    value_string: str | None = None
    value_int: int | None = None
    value_float: float | None = None
    value_bool: bool | None = None


class AttributeShortPublic(BaseModel):
    id: int
    code: str
    name: str
    unit: str | None = None
    data_type: AttributeDataType

    model_config = ConfigDict(from_attributes=True)

class ProductAttributePublic(BaseModel):
    id: int
    attribute_id: AttributeShortPublic

    value_string: str | None = None
    value_int: int | None = None
    value_float: float | None = None
    value_bool: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(ProductBase):
    attributes: list[ProductAttributeValueIn] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    title: constr(max_length=100) | None = None
    description: str | None = Field(default=None, max_length=500)
    price: conint(ge=0) | None = None
    quantity: conint(ge=0) | None = None
    attributes: list[ProductAttributeValueIn] | None = None
    is_active: bool | None = None

class ProductPublic(ProductBase):
    id: int
    shop_id: int
    article: str

    fires_count: int
    reviews_count: int
    rating_avg: float | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class ProductAdminPublic(ProductBase):
    is_blocked: bool
    blocked_reason: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BlockProductPayload(BaseModel):
    reason: str



