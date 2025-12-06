from pydantic import BaseModel, constr, Field, conint, ConfigDict


class ProductBase(BaseModel):
    title: constr(max_length=100)
    description: str = Field(..., max_length=500)
    price: conint(ge=0)
    quantity: conint(ge=0) = 1

class ProductCreate(ProductBase):
    shop_id: int
    article: constr(max_length=16)

class ProductUpdate(BaseModel):
    title: constr(max_length=100) | None = None
    description: str = Field(..., max_length=500)
    price: conint(ge=0)
    quantity: conint(ge=0) = 1
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

