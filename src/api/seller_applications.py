from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from src.api.dependencies import DBDep, UserIdDep
from src.models.seller_applications import SellerApplicationsOrm
from src.schemas.enums import SellerApplicationsStatus, ShopStatus
from src.schemas.seller_applications import SellerApplicationOut, SellerApplicationCreate

router = APIRouter(prefix="/applications", tags=["Заявка на продавца"])

@router.post("", response_model=SellerApplicationOut)
async def create_seller_application(
        payload: SellerApplicationCreate,
        db: DBDep,
        user: UserIdDep
):
    stmt = (
        select(SellerApplicationsOrm)
        .filter(
    SellerApplicationsOrm.user_id == user,
            SellerApplicationsOrm.status == SellerApplicationsStatus.pending,
        )
        .limit(1)
    )
    existing = (await db.session.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="У вас уже есть заявка на рассмотрении"
        )

    app_obj = SellerApplicationsOrm(
        user_id=user,
        fio=payload.fio,
        phone_number=payload.phone_number,
        inn=payload.inn,
        business_type=payload.business_type,
        shop_type=payload.shop_type,
        shop_name=payload.shop_name,
        description=payload.description,
        avatar_url=payload.avatar_url,
        city=payload.city,
        social_links=payload.social_links,
        status=SellerApplicationsStatus.pending,
    )

    db.session.add(app_obj)
    await db.commit()
    await db.session.refresh(app_obj)
    return app_obj

@router.get("/my", response_model=SellerApplicationOut | None)
async def get_my_seller_application(
        db: DBDep,
        user_id: UserIdDep,
        status: ShopStatus
):
    stmt = (
        select(SellerApplicationsOrm)
        .filter(SellerApplicationsOrm.user_id == user_id)
        .order_by(SellerApplicationsOrm.created_at.desc())
        .limit(1)
    )
    app_obj = (await db.session.execute(stmt)).scalar_one_or_none()
    return app_obj
