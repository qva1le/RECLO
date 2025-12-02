from fastapi import HTTPException
from sqlalchemy import select

from src.models.shops import ShopsOrm
from src.schemas.enums import ShopStatus, BusinessType, ShopType
from src.schemas.shops import ShopEditUser
from src.services.base import BaseService


class ShopsService(BaseService):
    async def get_my_shop_user(self, user_id: int) -> ShopsOrm:
        shop = await self.db.shops.get_one_or_none(owner_id=user_id)
        if not shop or getattr(shop, "status", None) == ShopStatus.blocked:
            raise HTTPException(status_code=404, detail="Магазин не найден или заблокирован")
        return shop

    async def edit_my_shop(self, user_id: int, data: ShopEditUser):
        shop = await self.db.shops.get_one_or_none(owner_id=user_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Магазин не найден или заблокирован")

        update_data = data.dict()
        if not update_data:
            raise HTTPException(status_code=400, detail="Нет данных для обновления")

        for f in ("id", "owner_id", "application_id", "status", "created_at", "updated_at"):
            update_data.pop(f, None)

        await self.db.shops.edit(update_data, id=shop.id)
        await self.db.commit()

        return await self.db.shops.get_one(id=shop.id)


    async def delete_my_shop(self, user_id: int):
        shop = await self.db.shops.get_one_or_none(owner_id=user_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Магазин не найден или заблокирован")

        await self.db.shops.delete(id=shop.id)
        await self.db.commit()


    async def get_shop_admin(self, user_id: int) -> ShopsOrm:
        shop = await self.db.shops.get_one_or_none(id=user_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Магазин не найден или заблокирован")
        return shop


    async def get_shops(self, limit: int | None = None, offset: int | None = None, **filters):
        return await self.db.shops.get_all(limit=limit, offset=offset,**filters)


    async def get_all_shops_public(self, shop_type: ShopType | None = None):
        filters = {
            "status": ShopStatus.active,
        }

        if shop_type is not None:
            filters["shop_type"] = shop_type

        shops = await self.db.shops.get_all(limit=10000, offset=0, **filters)
        return shops


    async def get_all_shops_admin(
            self, limit: int | None = None,
            offset: int | None = None,
            owner_id: int | None = None,
            application_id: int | None = None,
            city: str | None = None,
            business_type: BusinessType | None = None,
            shop_type: ShopType | None = None,
            status: ShopStatus | None = None
    ) -> ShopsOrm:
        filters: dict = {}

        if owner_id is not None:
            filters["owner_id"] = owner_id
        if application_id is not None:
            filters["application_id"] = application_id
        if city is not None:
            filters["city"] = city
        if business_type is not None:
            filters["business_type"] = business_type
        if shop_type is not None:
            filters["shop_type"] = shop_type
        if status is not None:
            filters["status"] = status

        shops = await self.db.shops.get_all(
            limit=limit,
            offset=offset,
            **filters,
        )
        return shops

    async def get_shops_public(self, city: str | None = None):
        filters = {"status": ShopStatus.active}
        if city is not None:
            filters["city"] = city
        return await self.get_shops(city=city)

    async def block_shop(self,  shop_id: int):
        stmt = select(ShopsOrm).filter(ShopsOrm.id == shop_id)
        res = await self.db.session.execute(stmt)
        shop = res.scalar_one_or_none()

        if shop is None:
            raise HTTPException(status_code=404, detail="Магазин не найден")

        if shop.status == ShopStatus.blocked:
            raise HTTPException(status_code=400, detail="Магазин уже заблокирован")

        shop.status = ShopStatus.blocked

        await self.db.session.commit()
        await self.db.session.refresh(shop)

        return shop

    async def unblock_shop(self, shop_id: int):
        stmt = select(ShopsOrm).filter(ShopsOrm.id == shop_id)
        res = await self.db.session.execute(stmt)
        shop = res.scalar_one_or_none()

        if shop is None:
            raise HTTPException(status_code=404, detail="Магазин не найден")

        if shop.status == ShopStatus.active:
            raise HTTPException(status_code=400, detail="Магазин уже разблокирован")

        shop.status = ShopStatus.active

        await self.db.session.commit()
        await self.db.session.refresh(shop)

        return shop




