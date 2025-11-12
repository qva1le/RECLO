from fastapi import APIRouter
from sqlalchemy import select

from src.api.dependencies import DBDep
from src.models.seller_applications import SellerApplicationsOrm
from src.schemas.enums import SellerApplicationsStatus
from src.schemas.seller_applications import SellerApplicationOut, SellerApplicationCreate

router = APIRouter(prefix="/admin/seller-applications", tags=["Админка для заявок"])

@router.get("", response_model=list[SellerApplicationOut])
async def list_seller_applications(db: DBDep, status: SellerApplicationsStatus | None = None):
    stmt = select(SellerApplicationsOrm).order_by(SellerApplicationsOrm.created_at.desc())

    if status:
        stmt = stmt.filter(SellerApplicationsOrm.status == status)

    result = (await db.session.execute(stmt)).scalars().all()
    return result




