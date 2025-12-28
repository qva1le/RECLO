from fastapi import APIRouter, Depends
from sqlalchemy.testing import db

from src.api.dependencies import DBDep, require_admin
from src.schemas.products import ProductAdminPublic, ProductUpdate, BlockProductPayload
from src.services.products import ProductsService

router = APIRouter(prefix="/admin/products", tags=["Админка для товаров"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[ProductAdminPublic])
async def list_products_admin(
        db: DBDep,
        limit: int = 100,
        offset: int = 0,
        shop_id: int | None = None,
        owner_id: int | None = None,
        only_blocked: bool | None = None,
        only_active: bool | None = None
):
    service = ProductsService(db)
    products = await service.admin_list_products(
        limit=limit,
        offset=offset,
        shop_id=shop_id,
        owner_id=owner_id,
        only_blocked=only_blocked,
        only_active=only_active,
    )

    return products

@router.get("/{product_id}", response_model=ProductAdminPublic)
async def get_product_admin(product_id: int, db: DBDep):
    service = ProductsService(db)
    product = await service.admin_get_product(product_id=product_id)
    return product


@router.patch("/{product_id}", response_model=ProductAdminPublic)
async def admin_update_product(db: DBDep, product_id: int, payload: ProductUpdate):
    service = ProductsService(db)
    product = await service.admin_update_product(product_id=product_id, payload=payload)
    return product


@router.post("/{product_id}/block", response_model=ProductAdminPublic)
async def admin_block_product(product_id: int, payload:BlockProductPayload, db: DBDep):
    service = ProductsService(db)
    product = await service.admin_block_product(product_id=product_id, reason=payload.reason)
    return product


@router.post("/{product_id}/unblock", response_model=ProductAdminPublic)
async def admin_unblock_product(product_id: int, db: DBDep):
    service = ProductsService(db)
    product = await service.admin_unblock_product(product_id=product_id)
    return product


@router.delete("/{product_id}")
async def admin_delete_product(product_id: int, db: DBDep):
    service =ProductsService(db)
    await service.admin_delete_product(product_id=product_id)
    return