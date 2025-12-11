from pydantic import BaseModel, constr, Field, conint, ConfigDict


class ProductBase(BaseModel):
    title: constr(max_length=100)
    description: str = Field(..., max_length=500)
    price: conint(ge=0)
    quantity: conint(ge=0) = 1

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: constr(max_length=100) | None = None
    description: str | None = Field(default=None, max_length=500)
    price: conint(ge=0) | None = None
    quantity: conint(ge=0) | None = None
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



