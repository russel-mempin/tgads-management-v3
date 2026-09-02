import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.crud.misc_sale import (
    archive_misc_sale,
    create_misc_sale,
    get_all_misc_sales,
    update_misc_sale,
)
from app.database import get_session
from app.enums import UserRoles
from app.models import MiscSale, MiscSaleBase, User
from app.schemas.misc_sale import MiscSaleCreate, MiscSalePublic
from app.services.dependencies import get_current_active_user

router = APIRouter(
    prefix="/misc-sales", tags=["misc-sales"], dependencies=[Depends(get_current_active_user)]
)


@router.get("/", response_model=list[MiscSalePublic])
def read_all(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    db: Session = Depends(get_session),
    include_archived: bool = False,
    current_user: User = Depends(get_current_active_user),
):
    if include_archived and current_user.role != UserRoles.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can include archived records.",
        )
    return get_all_misc_sales(db, include_archived, offset=offset, limit=limit)


@router.post("/")
def create(
    data: MiscSaleCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return create_misc_sale(db, data, current_user.id)


@router.patch("/{misc_sale_id}", response_model=MiscSale)
def update(
    misc_sale_id: uuid.UUID,
    data: MiscSaleBase,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return update_misc_sale(db, misc_sale_id, data, current_user.id)


@router.patch("/{misc_sale_id}/archive")
def archive(
    misc_sale_id: uuid.UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return archive_misc_sale(db, misc_sale_id, current_user.id)
