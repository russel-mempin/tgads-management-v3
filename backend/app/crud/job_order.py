import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import String, cast, func, or_
from sqlmodel import Session, col, select

from app.enums import JobStatus, PaymentStatus, SizeUnit
from app.models import (
    Account,
    AuditLog,
    ClaimingHistory,
    Customer,
    ExtraService,
    JobItem,
    JobItemExtra,
    JobOrder,
    Payment,
    Service,
    ServiceOption,
)
from app.schemas.job_order import (
    ClaimCreate,
    JobItemCreate,
    JobItemExtraCreate,
    JobItemUpdate,
    JobOrderCreate,
    PaymentCreate,
    PricingData,
)
from app.utils.utils import compute_unit_price


def _get_service_data_from_option(db: Session, option_id: uuid.UUID):
    option = db.get(ServiceOption, option_id)
    if not option:
        raise HTTPException(status_code=404, detail="Variant not found.")
    service = option.service
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")
    return option, service


def _get_extra_service_data_by_id(db: Session, extra_id: uuid.UUID):
    extra = db.get(ExtraService, extra_id)
    if not extra:
        raise HTTPException(status_code=404, detail="Extra service not found.")
    return extra


def _get_account_by_id(db: Session, account_id: uuid.UUID):
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")
    return account


def _get_job_order_by_id(db: Session, job_order_id: uuid.UUID):
    job_order = db.get(JobOrder, job_order_id)
    if not job_order:
        raise HTTPException(status_code=404, detail="Job order not found.")
    return job_order


def _get_job_item_by_item_id(db: Session, item_id: str):
    job_item = db.exec(select(JobItem).where(JobItem.item_id == item_id)).first()
    if not job_item:
        raise HTTPException(status_code=404, detail="Job item not found.")
    return job_item


def _build_job_item(
    db: Session, job_order_id: uuid.UUID, data: JobItemCreate
) -> JobItem:
    option, service = _get_service_data_from_option(db, data.service_option_id)
    return JobItem(
        description=data.description,
        discount_amount=data.discount_amount,
        due_date=data.due_date,
        extra_charge=data.extra_charge,
        height=data.height,
        item_id=data.item_id,
        job_status=data.job_status,
        notes=data.notes,
        quantity=data.quantity,
        service_abbreviation_snapshot=service.abbreviation,
        service_option_name_snapshot=option.name,
        service_name_snapshot=service.name,
        size_unit=data.size_unit,
        subtotal=data.subtotal,
        unit_price=data.unit_price,
        width=data.width,
        job_order_id=job_order_id,
        service_id=service.id,
        service_option_id=option.id,
    )


def _build_job_item_extra(
    db: Session, job_item_id: uuid.UUID, data: JobItemExtraCreate
) -> JobItemExtra:
    extra_service = _get_extra_service_data_by_id(db, data.extra_service_id)
    return JobItemExtra(
        job_item_id=job_item_id,
        extra_service_id=extra_service.id,
        quantity=data.quantity,
        name_snapshot=extra_service.name,
        price_snapshot=extra_service.price,
    )


def _build_payment(db: Session, job_order_id: uuid.UUID, data: PaymentCreate) -> Payment:
    account = _get_account_by_id(db, data.account_id)
    return Payment(
        date_received=data.date_received,
        reference_number=data.reference_number,
        amount=data.amount,
        notes=data.notes,
        account_name_snapshot=account.name,
        account_id=account.id,
        job_order_id=job_order_id,
    )


def _build_claiming_history(db: Session, job_order_id: uuid.UUID, item_id: str, data: ClaimCreate) -> ClaimingHistory:
    job_item = _get_job_item_by_item_id(db, item_id)
    return ClaimingHistory(
        date_claimed=data.date_claimed,
        name=data.name,
        pcs_claimed=data.pcs_claimed,
        job_order_id=job_order_id,
        job_item_id=job_item.id,
        claimed_item_id=data.claimed_item_id,
    )


def get_all_job_orders(
    db: Session,
    offset: int = 0,
    limit: int = 100,
    include_archived: bool = False,
    payment_status: PaymentStatus | None = None,
    job_status: JobStatus | None = None,
    search: str | None = None,
) -> list[JobOrder]:
    query = select(JobOrder).outerjoin(
        Customer, col(JobOrder.customer_id) == col(Customer.id)
    )

    if not include_archived:
        query = query.where(JobOrder.is_active)

    if payment_status:
        query = query.where(JobOrder.payment_status == payment_status)

    if job_status:
        query = query.where(JobOrder.overall_job_status == job_status)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                col(Customer.name).ilike(search_term),
                cast(JobOrder.jo_number, String).ilike(search_term),
            )
        )

    return list(
        db.exec(
            query.order_by(col(JobOrder.jo_number).desc()).offset(offset).limit(limit)
        ).all()
    )


def get_job_order_count(
    db: Session,
    include_archived: bool = False,
    payment_status: PaymentStatus | None = None,
    job_status: JobStatus | None = None,
    search: str | None = None,
) -> int:
    query = (
        select(func.count())
        .select_from(JobOrder)
        .outerjoin(Customer, col(JobOrder.customer_id) == col(Customer.id))
    )

    if not include_archived:
        query = query.where(JobOrder.is_active)
    if payment_status:
        query = query.where(JobOrder.payment_status == payment_status)
    if job_status:
        query = query.where(JobOrder.overall_job_status == job_status)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                col(Customer.name).ilike(search_term),
                cast(JobOrder.jo_number, String).ilike(search_term),
            )
        )

    return db.exec(query).one()


def get_job_order(db: Session, job_order_id: uuid.UUID) -> JobOrder:
    job_order = db.exec(select(JobOrder).where(JobOrder.id == job_order_id)).first()
    if not job_order:
        raise HTTPException(
            status_code=404,
            detail="Job order not found.",
        )
    return job_order


def get_price(
    db: Session,
    height: float | None,
    width: float | None,
    service_id: uuid.UUID,
    option_id: uuid.UUID,
    size_unit: SizeUnit | None,
    quantity: int,
) -> PricingData:
    service = db.exec(select(Service).where(Service.id == service_id)).first()

    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    service_option = db.exec(
        select(ServiceOption).where(ServiceOption.id == option_id)
    ).first()

    if service_option is None:
        raise HTTPException(status_code=404, detail="Service option not found")

    return compute_unit_price(
        height, width, service, service_option, size_unit, quantity
    )


def create_job_order(db: Session, data: JobOrderCreate, current_user_id: uuid.UUID):
    try:
        jo_number_unique = db.exec(
            select(JobOrder).where(JobOrder.jo_number == data.jo_number)
        ).first()
        if jo_number_unique:
            raise HTTPException(
                status_code=409,
                detail=f"Job with JO Number {data.jo_number} already exists.",
            )
        if data.customer_info is not None:
            if data.customer_info.id is not None and data.customer_info.id != "":
                # Existing customer
                customer = db.get(Customer, data.customer_info.id)
                if customer is None:
                    raise HTTPException(status_code=404, detail="Customer not found.")

            elif data.customer_info.name and data.customer_info.name.strip():
                # New customer
                existing = db.exec(
                    select(Customer).where(
                        func.lower(Customer.name)
                        == data.customer_info.name.strip().lower()
                    )
                ).first()
                if existing:
                    customer = existing
                else:
                    customer = Customer(
                        name=data.customer_info.name.strip(),
                        address=data.customer_info.address.strip()
                        if data.customer_info.address
                        else None,
                        contact_no=data.customer_info.contact_no.strip()
                        if data.customer_info.contact_no
                        else None,
                        email=data.customer_info.email.strip()
                        if data.customer_info.email
                        else None,
                    )
                    db.add(customer)
                    db.flush()
            else:
                raise HTTPException(
                    status_code=422,
                    detail="Customer info must include either an existing customer ID or a name for a new customer.",
                )
        else:
            customer = None

        job_order = JobOrder(
            jo_number=data.jo_number,
            date_received=data.date_received,
            customer_id=customer.id if customer else None,
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )
        db.add(job_order)
        db.flush()

        for item in data.job_items:
            job_item = _build_job_item(db, job_order.id, item)
            db.add(job_item)
            db.flush()
            if item.extras:
                for extra in item.extras:
                    db.add(_build_job_item_extra(db, job_item.id, extra))
        if data.payments:
            for payment in data.payments:
                db.add(_build_payment(db, job_order.id, payment))
        if data.claiming_history:
            for claim in data.claiming_history:
                db.add(_build_claiming_history(db, job_order.id, claim.claimed_item_id, claim))
        db.flush()
        job_order.sync_computed_fields()

        audit = AuditLog(
            action=f"Created job order {job_order.jo_number}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        db.refresh(job_order)
        return job_order
    except Exception:
        db.rollback()
        raise


def archive_job_order(db: Session, jo_number: int, current_user_id: uuid.UUID):
    try:
        job_order = db.exec(
            select(JobOrder).where(JobOrder.jo_number == jo_number)
        ).first()
        if not job_order:
            raise HTTPException(
                status_code=404, detail=f"Job order with number {jo_number} not found"
            )

        job_order.is_active = False
        db.add(job_order)

        audit = AuditLog(
            action=f"Deleted job order {job_order.jo_number}", user_id=current_user_id
        )
        db.add(audit)

        db.commit()
        db.refresh(job_order)
        return "Job order deleted."
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def create_job_item(
    db: Session,
    job_order_id: uuid.UUID,
    data: JobItemCreate,
    current_user_id: uuid.UUID,
):
    try:
        job_order = db.exec(select(JobOrder).where(JobOrder.id == job_order_id)).first()
        if not job_order:
            raise HTTPException(
                status_code=404,
                detail="Job order not found.",
            )
        job_item = _build_job_item(db, job_order_id, data)
        db.add(job_item)
        db.flush()
        if data.extras:
            for extra in data.extras:
                job_extra = _build_job_item_extra(db, job_item.id, extra)
                db.add(job_extra)
        db.flush()
        job_order.sync_computed_fields()

        audit = AuditLog(
            action=f"Created job item {job_item.item_id}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        db.refresh(job_order)
        return job_order

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def update_job_item(
    db: Session, id: uuid.UUID, data: JobItemUpdate, current_user_id: uuid.UUID
):
    try:
        job_item = db.exec(select(JobItem).where(JobItem.id == id)).first()

        if not job_item:
            raise HTTPException(
                status_code=404,
                detail="Job item not found.",
            )

        new_extras = []

        # Update basic fields
        if data.quantity is not None:
            job_item.quantity = data.quantity

        if data.job_status is not None:
            job_item.job_status = data.job_status

        if data.notes is not None:
            job_item.notes = data.notes

        if data.extra_charge is not None:
            job_item.extra_charge = data.extra_charge

        if data.discount_amount is not None:
            job_item.discount_amount = data.discount_amount

        # Replace extras only when extras was included in the request
        if data.extras is not None:
            for existing_extra in job_item.extras:
                db.delete(existing_extra)

            for extra in data.extras:
                job_item_extra = _build_job_item_extra(db, job_item.id, extra)
                db.add(job_item_extra)
                new_extras.append(job_item_extra)
            # Make sure the new extras are available for extras total calculation
            db.flush()

        if job_item.job_status == JobStatus.CANCELLED:
            job_item.subtotal = 0

        else:
            option, service = _get_service_data_from_option(
                db, job_item.service_option_id
            )

            # Recalculate pricing
            pricing = compute_unit_price(
                job_item.height,
                job_item.width,
                service,
                option,
                job_item.size_unit,
                job_item.quantity,
            )

            # Recalculate extras
            extra_total = sum(e.price_snapshot * e.quantity for e in new_extras)

            job_item.unit_price = pricing.unit_price

            # Recalculate subtotal
            job_item.subtotal = (
                (job_item.unit_price * job_item.quantity)
                + extra_total
                + (job_item.extra_charge * job_item.quantity)
                - job_item.discount_amount
            )

        # Sync parent JobOrder before committing
        job_order = job_item.job_order
        job_order.sync_computed_fields()

        # Audit
        audit = AuditLog(
            action=f"Updated job item {job_item.item_id}",
            user_id=current_user_id,
        )
        db.add(audit)

        # One transaction
        db.commit()

        db.refresh(job_item)

        return job_item

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def get_business_kpis(db: Session) -> dict:
    # Outstanding balance — sum of (total_due - total_paid) for unpaid/partial orders
    job_orders = db.exec(
        select(JobOrder).where(
            JobOrder.is_active,
            col(JobOrder.payment_status).in_(
                [PaymentStatus.UNPAID, PaymentStatus.PARTIAL]
            ),
        )
    ).all()
    outstanding_balance = sum(jo.total_due - jo.total_paid for jo in job_orders)

    # Count of unpaid orders
    unpaid_count = db.exec(
        select(func.count())
        .select_from(JobOrder)
        .where(JobOrder.is_active, JobOrder.payment_status == PaymentStatus.UNPAID)
    ).one()

    # Count of overdue jobs — job items past due_date and not released/cancelled
    now = datetime.now(UTC)
    overdue_count = db.exec(
        select(func.count())
        .select_from(JobItem)
        .where(
            JobItem.due_date < now,
            col(JobItem.job_status).not_in([JobStatus.RELEASED, JobStatus.CANCELLED]),
        )
    ).one()

    # Payments this week
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    payments_this_week = db.exec(
        select(func.sum(Payment.amount)).where(Payment.date_received >= week_start)
    ).one()

    return {
        "outstanding_balance": outstanding_balance,
        "unpaid_count": unpaid_count,
        "overdue_count": overdue_count,
        "payments_this_week": payments_this_week or 0.0,
    }


def get_operation_kpis(db: Session) -> dict:
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Count of overdue jobs — past due date, not released/cancelled
    overdue_count = db.exec(
        select(func.count(col(JobOrder.id).distinct()))
        .select_from(JobOrder)
        .join(JobItem, col(JobOrder.id) == col(JobItem.job_order_id))
        .where(
            JobItem.due_date < now,
            col(JobItem.job_status).not_in(
                [
                    JobStatus.RELEASED,
                    JobStatus.CANCELLED,
                    JobStatus.FOR_PICKUP,
                ]
            ),
            JobOrder.is_active,
        )
    ).one()

    # Count of jobs due today — due date is within today, not released/cancelled
    due_today_count = db.exec(
        select(func.count(col(JobOrder.id).distinct()))
        .select_from(JobOrder)
        .join(JobItem, col(JobOrder.id) == col(JobItem.job_order_id))
        .where(
            JobItem.due_date >= today_start,
            JobItem.due_date < today_end,
            col(JobItem.job_status).not_in(
                [
                    JobStatus.RELEASED,
                    JobStatus.CANCELLED,
                    JobStatus.FOR_PICKUP,
                ]
            ),
            JobOrder.is_active,
        )
    ).one()

    # Count of jobs in progress
    in_progress_count = db.exec(
        select(func.count())
        .select_from(JobOrder)
        .where(
            col(JobOrder.overall_job_status).not_in(
                [
                    JobStatus.RELEASED,
                    JobStatus.CANCELLED,
                    JobStatus.FOR_PICKUP,
                ]
            ),
            JobOrder.is_active,
        )
    ).one()

    # Count of jobs ready for pickup — released but not fully claimed
    ready_for_pickup_count = db.exec(
        select(func.count())
        .select_from(JobOrder)
        .where(
            JobOrder.overall_job_status == JobStatus.FOR_PICKUP,
            JobOrder.is_active,
        )
    ).one()

    return {
        "overdue_jobs": overdue_count,
        "due_today": due_today_count,
        "in_progress": in_progress_count,
        "ready_for_pickup": ready_for_pickup_count,
    }


def get_jobs_with_outstanding_balance(db: Session) -> list[JobOrder]:
    return list(
        db.exec(
            select(JobOrder).where(
                JobOrder.is_active,
                col(JobOrder.payment_status).in_(
                    [PaymentStatus.UNPAID, PaymentStatus.PARTIAL]
                ),
            )
        ).all()
    )


def get_unpaid_job_orders(db: Session) -> list[JobOrder]:
    return list(
        db.exec(
            select(JobOrder).where(
                JobOrder.is_active,
                JobOrder.payment_status == PaymentStatus.UNPAID,
            )
        ).all()
    )


def get_overdue_job_orders(db: Session) -> list[JobOrder]:
    now = datetime.now(UTC)
    overdue_job_order_ids = db.exec(
        select(JobItem.job_order_id).where(
            JobItem.due_date < now,
            col(JobItem.job_status).not_in([JobStatus.RELEASED, JobStatus.CANCELLED]),
        )
    ).all()
    return list(
        db.exec(
            select(JobOrder).where(
                col(JobOrder.id).in_(overdue_job_order_ids),  # ← wrap with col()
                JobOrder.is_active,
            )
        ).all()
    )


def get_jobs_with_payments_this_week(db: Session) -> list[JobOrder]:
    now = datetime.now(UTC)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    job_order_ids = db.exec(
        select(Payment.job_order_id).where(Payment.date_received >= week_start)
    ).all()

    return list(
        db.exec(
            select(JobOrder).where(
                col(JobOrder.id).in_(job_order_ids), JobOrder.is_active
            )
        ).all()
    )


def get_overdue_jobs(db: Session) -> list[JobOrder]:
    now = datetime.now(UTC)
    return list(
        db.exec(
            select(JobOrder)
            .join(JobItem, col(JobOrder.id) == col(JobItem.job_order_id))
            .where(
                JobItem.due_date < now,
                col(JobItem.job_status).not_in(
                    [
                        JobStatus.RELEASED,
                        JobStatus.CANCELLED,
                        JobStatus.FOR_PICKUP,
                    ]
                ),
                JobOrder.is_active,
            )
            .distinct()
            .order_by(col(JobOrder.jo_number).desc())
        ).all()
    )


def get_jobs_in_progress(db: Session) -> list[JobOrder]:
    return list(
        db.exec(
            select(JobOrder)
            .where(
                col(JobOrder.overall_job_status).not_in(
                    [
                        JobStatus.RELEASED,
                        JobStatus.CANCELLED,
                        JobStatus.FOR_PICKUP,
                    ]
                ),
                JobOrder.is_active,
            )
            .order_by(col(JobOrder.jo_number).desc())
        ).all()
    )


def get_jobs_due_today(db: Session) -> list[JobOrder]:
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    return list(
        db.exec(
            select(JobOrder)
            .join(JobItem, col(JobOrder.id) == col(JobItem.job_order_id))
            .where(
                JobItem.due_date >= today_start,
                JobItem.due_date < today_end,
                col(JobItem.job_status).not_in(
                    [
                        JobStatus.RELEASED,
                        JobStatus.CANCELLED,
                        JobStatus.FOR_PICKUP,
                    ]
                ),
                JobOrder.is_active,
            )
            .distinct()
            .order_by(col(JobOrder.jo_number).desc())
        ).all()
    )


def get_jobs_ready_for_pickup(db: Session) -> list[JobOrder]:
    return list(
        db.exec(
            select(JobOrder)
            .join(JobItem, col(JobOrder.id) == col(JobItem.job_order_id))
            .where(JobItem.job_status == JobStatus.FOR_PICKUP, JobOrder.is_active)
            .distinct()
        ).all()
    )
