from typing import List

from fastapi import APIRouter

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.products import ProductCreate, ProductPublic, ProductUpdate
from src.services.products import ProductsService

router = APIRouter(prefix="/products", tags=["Товары"])

@router.post("", response_model=ProductPublic, summary="Для всех")
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


@router.post("/{product_id}/deactivate")
async def deactivate_product(product_id: int, db: DBDep, user_id: UserIdDep):
    service = ProductsService(db)
    await service.deactivate_product_for_owner(product_id=product_id, user_id=user_id)
    return


@router.post("/{product_id}/activate")
async def activate_product(product_id: int, db: DBDep, user_id: UserIdDep):
    service = ProductsService(db)
    await service.activate_product_for_owner(product_id=product_id, user_id=user_id)
    return


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: DBDep, user_id: UserIdDep):
    service = ProductsService(db)
    await service.delete_product_for_owner(product_id=product_id, user_id=user_id)
    return


@router.get("/{product_id}", response_model=ProductPublic, summary="Карточка товара")
async def get_product_public(product_id: int, db: DBDep):
    service = ProductsService(db)
    product = await service.get_product_public(product_id=product_id)
    return product


@router.get("",response_model=List[ProductPublic])
async def list_product_public(db: DBDep, limit: int = 100, offset: int = 0):
    service = ProductsService(db)
    products = await service.list_products_public(limit=limit, offset=offset)
    return products
