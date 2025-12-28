from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select

from src.api.dependencies import DBDep, require_admin
from src.models.seller_applications import SellerApplicationsOrm
from src.models.shops import ShopsOrm
from src.schemas.enums import SellerApplicationsStatus, ShopStatus
from src.schemas.seller_applications import SellerApplicationOut, SellerApplicationCreate, SellerApplicationsReview

router = APIRouter(prefix="/admin/seller-applications", tags=["Админка для заявок"], dependencies=[Depends(require_admin)])

@router.get("", response_model=list[SellerApplicationOut])
async def list_seller_applications(db: DBDep, status: SellerApplicationsStatus | None = None):
    stmt = select(SellerApplicationsOrm).order_by(SellerApplicationsOrm.created_at.desc())

    if status:
        stmt = stmt.filter(SellerApplicationsOrm.status == status)

    result = (await db.session.execute(stmt)).scalars().all()
    return result

@router.post("/review/{application_id}", response_model=SellerApplicationOut)
async def review_seller_application(
        application_id: int,
        payload: SellerApplicationsReview,
        db: DBDep
):
    stmt = select(SellerApplicationsOrm).filter(
        SellerApplicationsOrm.id ==application_id
    )
    res = await db.session.execute(stmt)
    application: SellerApplicationsOrm | None = res.scalar_one_or_none()

    if application is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    if application.status != SellerApplicationsStatus.pending:
        raise HTTPException(status_code=400, detail="Это заявка была уже рассмотрена")

    if not payload.approve:
        if not payload.rejection_reason:
            raise HTTPException(status_code=400, detail="Требуется указать причину отказа")

        application.status = SellerApplicationsStatus.rejected
        application.rejection_reason = payload.rejection_reason
        application.reviewed_at = datetime.utcnow()

        await db.commit()
        await db.session.refresh(application)
        return application

    stmt_shop = select(ShopsOrm).filter(
        ShopsOrm.owner_id == application.user_id
    ).limit(1)
    existing_shop = (await db.session.execute(stmt_shop)).scalar_one_or_none()
    if existing_shop:
        raise HTTPException(status_code=400, detail="У пользователя уже существует магазин")

    shop = ShopsOrm(
        owner_id=application.user_id,
        application_id=application_id,
        name=application.shop_name,
        avatar_url=application.avatar_url,
        description=application.description,
        city=application.city,
        inn=application.inn,
        business_type=application.business_type,
        shop_type=application.shop_type,
        status=ShopStatus.active,
    )

    db.session.add(shop)

    application.status = SellerApplicationsStatus.approved
    application.reviewed_at = datetime.utcnow()
    application.rejection_reason = None

    await db.commit()
    await db.session.refresh(application)

    return application



