from select import select

from fastapi import APIRouter, HTTPException, Depends, Query, Response

from src.api.dependencies import DBDep, UserIdDep, ShopDep
from src.models.shops import ShopsOrm
from src.schemas.enums import ShopStatus, ShopType
from src.schemas.shops import ShopOut, ShopEditUser, ShopsPublic
from src.services.shops import ShopsService
from src.utils.db_manager import DBManager

router = APIRouter(prefix="/shops", tags=["Магазины"])


@router.get("", response_model=list[ShopsPublic])
async def get_all_shops(db: DBDep, shop_type: ShopType | None = Query(None)):
    shops = await ShopsService(db).get_all_shops_public(shop_type=shop_type)
    return [ShopsPublic.model_validate(shop, from_attributes=True) for shop in shops]



@router.get("/my_shop", response_model=ShopsPublic)
async def get_my_shop(
    db: DBDep,
    _shop: ShopDep,
    user_id: UserIdDep
):
    shop = await ShopsService(db).get_my_shop_user(user_id)
    return ShopsPublic.model_validate(shop, from_attributes=True)

@router.put("/my/edit_shop", response_model=ShopsPublic)
async def edit_my_shop(
        db: DBDep,
        _shop: ShopDep,
        user_id: UserIdDep,
        data: ShopEditUser
):
    shop = await ShopsService(db).edit_my_shop(user_id,  data)
    return ShopOut.model_validate(shop, from_attributes=True)

@router.delete("/my/delete_shop")
async def delete_my_shop(
        db: DBDep,
        _shop: ShopDep,
        user_id: UserIdDep
):
    await ShopsService(db).delete_my_shop(user_id)
    return Response(status_code=204)

