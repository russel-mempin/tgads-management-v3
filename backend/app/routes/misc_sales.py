import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.crud.misc_sale import (
    archive_misc_sale,
    create_misc_sale,
    get_all_misc_sales,
    get_misc_sales_count,
    update_misc_sale,
)
from app.database import get_session
from app.enums import DatePeriod, UserRoles
from app.models import MiscSale, User
from app.schemas.misc_sale import MiscSaleCreate, MiscSalePublic, MiscSaleUpdate
from app.services.dependencies import get_current_active_user

router = APIRouter(
    prefix="/misc-sales", tags=["misc-sales"]
)


@router.get("/", response_model=list[MiscSalePublic])
def read_all(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    search: str | None = None,
    date_period: DatePeriod = DatePeriod.ALL,
    db: Session = Depends(get_session),
    include_archived: bool = False,
    current_user: User = Depends(get_current_active_user),
):
    if include_archived and current_user.role != UserRoles.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can include archived records.",
        )

    return get_all_misc_sales(
        db,
        include_archived=include_archived,
        search=search,
        date_period=date_period,
        offset=offset,
        limit=limit,
    )


@router.get("/count", response_model=int)
def read_count(
    search: str | None = None,
    date_period: DatePeriod = DatePeriod.ALL,
    include_archived: bool = False,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if include_archived and current_user.role != UserRoles.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can include archived records.",
        )

    return get_misc_sales_count(
        db,
        include_archived=include_archived,
        search=search,
        date_period=date_period,
    )


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
    data: MiscSaleUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return update_misc_sale(db, misc_sale_id, data, current_user)


@router.patch("/{misc_sale_id}/archive")
def archive(
    misc_sale_id: uuid.UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return archive_misc_sale(db, misc_sale_id, current_user)
