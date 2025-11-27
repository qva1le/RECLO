from fastapi import APIRouter, Query

from src.api.dependencies import DBDep
from src.schemas.enums import ShopType, ShopStatus, BusinessType
from src.schemas.shops import ShopOut, ShopStatusChange
from src.services.shops import ShopsService

router = APIRouter(prefix="/admin/shops", tags=["Админка для магазинов"])

@router.get("/{shop_id}", response_model=ShopOut)
async def get_shop_admin(
        db: DBDep,
        shop_id: int
):
    shop = await ShopsService(db).get_shop_admin(shop_id)
    return shop

@router.get("", response_model=list[ShopOut])
async def list_shops_admin(
        db: DBDep,
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),

        owner_id: int | None = Query(None),
        application_id: int | None = Query(None),
        city: str | None = Query(None),
        business_type: BusinessType | None = Query(None),
        shop_type: ShopType | None = Query(None),
        status: ShopStatus | None = Query(None)
):
    shops = await ShopsService(db).get_all_shops_admin(
        limit=limit,
        offset=offset,
        owner_id=owner_id,
        application_id=application_id,
        city=city,
        business_type=business_type,
        shop_type=shop_type,
        status=status
    )

    return shops


@router.post("/{shop_id}/block", response_model=ShopStatusChange)
async def block_shop(shop_id: int, db: DBDep):
    shop = await ShopsService(db).block_shop(shop_id)
    return ShopStatusChange(status=shop.status)

@router.post("/{shop_id}/unblock", response_model=ShopStatusChange)
async def unblock_shop(shop_id: int, db: DBDep):
    shop = await ShopsService(db).unblock_shop(shop_id)
    return ShopStatusChange(status=shop.status)

