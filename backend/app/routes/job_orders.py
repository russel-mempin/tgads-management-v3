import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.job_order import (
    archive_job_order,
    create_job_item,
    create_job_order,
    get_all_job_orders,
    get_business_kpis,
    get_job_order,
    get_job_order_count,
    get_jobs_due_today,
    get_jobs_in_progress,
    get_jobs_ready_for_pickup,
    get_jobs_with_outstanding_balance,
    get_jobs_with_payments_this_week,
    get_operation_kpis,
    get_overdue_job_orders,
    get_overdue_jobs,
    get_price,
    get_unpaid_job_orders,
    update_job_item,
)
from app.database import get_session
from app.enums import JobStatus, PaymentStatus, SizeUnit, UserRoles
from app.models import User
from app.schemas.job_order import (
    JobItemCreate,
    JobItemUpdate,
    JobOrderCreate,
    JobOrderPublic,
    PricingData,
)
from app.services.dependencies import get_current_active_user

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
    filter: (
        str | None
    ) = None,  # outstanding, unpaid, overdue, payments-week, overdue, due-today, in-progress, for-pickup
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if filter == "outstanding":
        return get_jobs_with_outstanding_balance(db)
    elif filter == "unpaid":
        return get_unpaid_job_orders(db)
    elif filter == "overdue":
        return get_overdue_job_orders(db)
    elif filter == "payments-week":
        return get_jobs_with_payments_this_week(db)
    elif filter == "overdue-jobs":
        return get_overdue_jobs(db)
    elif filter == "in-progress":
        return get_jobs_in_progress(db)
    elif filter == "due-today":
        return get_jobs_due_today(db)
    elif filter == "for-pickup":
        return get_jobs_ready_for_pickup(db)
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
    current_user: User = Depends(get_current_active_user),
):
    return get_job_order_count(
        db,
        include_archived=include_archived and current_user.role == UserRoles.ADMIN,
        payment_status=payment_status,
        job_status=job_status,
        search=search,
    )


@router.get("/kpis")
def read_kpis(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    operational = get_operation_kpis(db)

    if current_user.role == UserRoles.OWNER:
        business = get_business_kpis(db)
        return {**operational, **business}

    return operational


@router.get("/compute-unit-price", response_model=PricingData)
def compute_unit_price_route(
    height: float | None,
    width: float | None,
    service_id: uuid.UUID,
    option_id: uuid.UUID,
    size_unit: SizeUnit | None,
    quantity: int,
    db: Session = Depends(get_session),
):
    return get_price(
        db, height=height, width=width, service_id=service_id, option_id=option_id, size_unit=size_unit, quantity=quantity
    )
    

@router.get("/{job_order_id}", response_model=JobOrderPublic)
def read_job_order(job_order_id: uuid.UUID, db: Session = Depends(get_session)):
    return get_job_order(db, job_order_id)


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


@router.post("/job-items/{job_order_id}")
def create_item(job_order_id: uuid.UUID, data: JobItemCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_job_item(db, job_order_id, data, current_user.id)


@router.patch("/job-items/{id}")
def update(
    id: uuid.UUID,
    data: JobItemUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return update_job_item(db, id, data, current_user.id)