import uuid

from fastapi import HTTPException
from sqlalchemy import select

from src.models.products import ProductsOrm
from src.models.shops import ShopsOrm
from src.schemas.products import ProductCreate, ProductUpdate
from src.services.base import BaseService


class ProductsService(BaseService):
    async def _get_shop_for_owner(self, user_id: int) -> ShopsOrm:
        stmt = select(ShopsOrm).filter(
                ShopsOrm.owner_id == user_id
        )
        res = await self.db.session.execute(stmt)
        shop =  res.scalar_one_or_none()

        if not shop:
            raise HTTPException(status_code=404, detail="Нет доступа к этому магазину или он не существует")
        return shop

    async def _get_product_for_owner(self, product_id: int, user_id: int) -> ProductsOrm:
        stmt = (
            select(ProductsOrm)
            .join(ShopsOrm, ShopsOrm.id == ProductsOrm.shop_id)
            .filter(
                ProductsOrm.id == product_id,
                ShopsOrm.owner_id == user_id,
            )
        )
        res = await self.db.session.execute(stmt)
        product = res.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден или нет доступа")
        return product


    async def _get_product_by_id(self, product_id: int, active_only: bool = False) -> ProductsOrm:
        stmt = select(ProductsOrm).filter(ProductsOrm.id == product_id)

        if active_only:
            stmt = stmt.filter(
                ProductsOrm.is_active.is_(True),
                ProductsOrm.is_blocked.is_(False),
            )

        res = await self.db.session.execute(stmt)
        product = res.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")

        return product

    async def create_product_for_owner(self, user_id: int, payload: ProductCreate) -> ProductsOrm:
        shop = await self._get_shop_for_owner(user_id=user_id)

        article = f"{shop.id}-{uuid.uuid4().hex[:8]}"


        stmt = select(ProductsOrm).filter(ProductsOrm.article == article)
        res = await self.db.session.execute(stmt)
        if res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Товар с таким артикулом уже существует")


        product = ProductsOrm(
            shop_id=shop.id,
            article=article,
            title=payload.title,
            description=payload.description,
            price=payload.price,
            quantity=payload.quantity,
        )

        self.db.session.add(product)
        await self.db.session.commit()
        await self.db.session.refresh(product)

        return product


    async def update_product_for_owner(self, user_id: int, product_id: int, payload: ProductUpdate) -> ProductsOrm:
        product = await self._get_product_for_owner(product_id, user_id)

        if product.is_blocked:
            raise HTTPException(
                status_code=403,
                detail="Товар заблокирован администрацией сайта. Действие недоступно, обратитесь в поддержку")

        data = payload.model_dump(exclude_unset=True)

        forbidden_fields = {"id", "shop_id", "article", "fires_count", "reviews_count", "rating_avg"}
        for field in forbidden_fields:
            data.pop(field, None)

        for field, value in  data.items():
            setattr(product, field, value)

        await self.db.session.commit()
        await self.db.session.refresh(product)

        return product


    async def deactivate_product_for_owner(self, user_id: int, product_id: int) -> None:
        product = await self._get_product_for_owner(product_id, user_id)

        if not product.is_active:
            return

        product.is_active = False

        if product.is_blocked:
            raise HTTPException(
                status_code=403,
                detail="Товар заблокирован администрацией сайта. Действие недоступно, обратитесь в поддержку")

        await self.db.session.commit()


    async def activate_product_for_owner(self, user_id: int, product_id: int) -> None:
        product = await self._get_product_for_owner(product_id, user_id)

        if product.is_blocked:
            raise HTTPException(
                status_code=403,
                detail="Товар заблокирован администрацией сайта. Действие недоступно, обратитесь в поддержку")

        if not product.is_active:
            return
        product.is_active = True

        await self.db.session.commit()


    async def delete_product_for_owner(self, product_id: int, user_id: int):
        product = await self._get_product_for_owner(product_id, user_id)

        if product.is_blocked:
            raise HTTPException(
                status_code=403,
                detail="Товар заблокирован администрацией сайта. Действие недоступно, обратитесь в поддержку")

        await self.db.session.delete(product)
        await self.db.session.commit()


    async def get_product_public(self, product_id: int) -> ProductsOrm:
        return await self._get_product_by_id(product_id, active_only=True)


    async def list_products_public(self, limit: int = 100, offset: int = 0) -> list[ProductsOrm]:
        stmt = (
            select(ProductsOrm)
            .filter(ProductsOrm.is_active.is_(True))
            .filter(ProductsOrm.is_blocked.is_(False))
            .order_by(ProductsOrm.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        res = await self.db.session.execute(stmt)
        products = res.scalars().all()

        return list(products)

