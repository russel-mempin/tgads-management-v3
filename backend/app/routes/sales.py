from app.models import MiscSale, MiscSaleBase, User
from typing import Annotated
from app.services.dependencies import get_current_active_user
from fastapi import APIRouter, Query, Depends
from sqlmodel import Session
from app.database import get_session
from app.crud.sale import get_all_misc_sales, create_misc_sale, update_misc_sale, archive_misc_sale
import uuid


router = APIRouter(prefix="/sales", tags=["sales"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[MiscSale])
def read_all(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_misc_sales(db, offset=offset, limit=limit)

@router.post("/", response_model=MiscSale)
def create(data: MiscSaleBase, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_misc_sale(db, data, current_user.id)

@router.patch("/{misc_sale_id}", response_model=MiscSale)
def update(misc_sale_id: uuid.UUID, data: MiscSaleBase, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_misc_sale(db, misc_sale_id, data, current_user.id)

@router.patch("/{misc_sale_id}/archive")
def archive(misc_sale_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return archive_misc_sale(db, misc_sale_id, current_user.id)