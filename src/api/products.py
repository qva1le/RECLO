from fastapi import APIRouter

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.products import ProductCreate, ProductPublic, ProductUpdate
from src.services.products import ProductsService

router = APIRouter(prefix="/products", tags=["Товары"])

@router.post("", response_model=ProductPublic)
async def create_product(payload: ProductCreate, db: DBDep, user_id: UserIdDep):
    service = ProductsService(db)
    product = await service.create_product_for_owner(
        user_id=user_id,
        payload=payload,
    )
    return product


@router.patch("/{product_id}", response_model=ProductPublic)
async def edit_product(payload: ProductUpdate, db: DBDep, user_id: UserIdDep, product_id: int):
    service = ProductsService(db)
    product = await service.update_product_for_owner(user_id=user_id, payload=payload, product_id=product_id)
    return product