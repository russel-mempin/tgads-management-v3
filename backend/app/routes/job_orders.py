from fastapi import APIRouter, Query, Depends
from app.schemas.job_order import JobOrderPublic
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.crud.job_order import (
    get_all_job_orders,
    get_job_order,
    get_price,
    create_job_order,
    archive_job_order,
    update_job_order,
    get_job_order_count
)
from app.schemas.job_order import JobOrderCreate
from app.services.dependencies import get_current_active_user
from app.models import User
from app.enums import UserRoles, SizeUnit, PaymentStatus, JobStatus
import uuid

router = APIRouter(
    prefix="/job-orders",
    tags=["job-orders"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_model=list[JobOrderPublic])
def read_all(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    include_archived: bool = False,
    payment_status: PaymentStatus | None = None,
    job_status: JobStatus | None = None,
    search: str | None = None,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return get_all_job_orders(
        db,
        offset=offset,
        limit=limit,
        include_archived=include_archived and current_user.role == UserRoles.ADMIN,
        payment_status=payment_status,
        job_status=job_status,
        search=search,
    )

@router.get("/count")
def read_job_order_count(
    include_archived: bool = False,
    payment_status: PaymentStatus | None = None,
    job_status: JobStatus | None = None,
    search: str | None = None,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    return get_job_order_count(
        db,
        include_archived=include_archived and current_user.role == UserRoles.ADMIN,
        payment_status=payment_status,
        job_status=job_status,
        search=search,
    )

@router.get("/compute-unit-price", response_model=float)
def compute_unit_price(
    height: float,
    width: float,
    service_name: str,
    size_unit: SizeUnit,
    db: Session = Depends(get_session),
):
    return get_price(
        db, height=height, width=width, service_name=service_name, size_unit=size_unit
    )


@router.get("/{jo_number}", response_model=JobOrderPublic)
def read_job_order(jo_number: int, db: Session = Depends(get_session)):
    return get_job_order(db, jo_number)


@router.post("/", response_model=JobOrderPublic)
def create(
    data: JobOrderCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return create_job_order(db, data, current_user.id)


@router.patch("/{jo_number}/archive")
def archive(
    jo_number: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return archive_job_order(db, jo_number, current_user.id)


@router.put("/{jo_number}")
def update(
    jo_number: int,
    data: JobOrderCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return update_job_order(db, jo_number, data, current_user.id)
