import uuid
from datetime import datetime, timedelta, timezone

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
from app.schemas.job_order import JobOrderCreate, PricingData
from app.utils.utils import compute_unit_price


def sync_job_order(db: Session, job_order: JobOrder) -> None:
    db.flush()
    print(len(job_order.job_items))
    print(len(job_order.payments))
    db.refresh(job_order)
    job_order.sync_computed_fields()


def get_all_job_orders(
    db: Session,
    offset: int = 0,
    limit: int = 100,
    include_archived: bool = False,
    payment_status: PaymentStatus | None = None,
    job_status: JobStatus | None = None,
    search: str | None = None,
) -> list[JobOrder]:
    query = select(JobOrder).join(
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
        .join(Customer, col(JobOrder.customer_id) == col(Customer.id))
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


def get_job_order_for_review(db: Session):
    return list(db.exec(select(JobOrder).where(JobOrder.for_review)).all())


def get_job_order(db: Session, jo_number: int) -> JobOrder:
    job_order = db.exec(select(JobOrder).where(JobOrder.jo_number == jo_number)).first()
    if not job_order:
        raise HTTPException(
            status_code=404,
            detail=f"Job order with JO number of {jo_number} not found.",
        )
    return job_order


def get_price(
    db: Session,
    height: float | None,
    width: float | None,
    service_id: uuid.UUID,
    option_id: uuid.UUID,
    size_unit: SizeUnit,
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
                        address=data.customer_info.address.strip(),
                        contact_no=data.customer_info.contact_no.strip(),
                        email=data.customer_info.email.strip(),
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
            option = db.get(ServiceOption, item.service_option_id)
            if not option:
                raise HTTPException(status_code=404, detail="Variant not found.")
            service = option.service
            if not service:
                raise HTTPException(status_code=404, detail="Service not found.")
            job_item = JobItem(
                job_order=job_order,
                description=item.description,
                discount_amount=item.discount_amount,
                due_date=item.due_date,
                extra_charge=item.extra_charge,
                height=item.height,
                item_id=item.item_id,
                job_status=item.job_status,
                notes=item.notes,
                service_option=option,
                quantity=item.quantity,
                service_abbreviation_snapshot=service.abbreviation,
                service_option_name_snapshot=option.name,
                service=service,
                service_name_snapshot=service.name,
                size_unit=item.size_unit,
                subtotal=item.subtotal,
                unit_price=item.unit_price,
                width=item.width,
            )
            db.add(job_item)
            if item.extras:
                for extra in item.extras:
                    extra_service = db.exec(
                        select(ExtraService).where(
                            ExtraService.id == extra.extra_service_id
                        )
                    ).first()
                    if not extra_service:
                        raise HTTPException(
                            status_code=404, detail="Extra service not found."
                        )
                    db.add(
                        JobItemExtra(
                            job_item=job_item,
                            extra_service_id=extra_service.id,
                            quantity=extra.quantity,
                            price_snapshot=extra_service.price,
                            name_snapshot=extra_service.name,
                        )
                    )
        if data.payments:
            for payment in data.payments:
                account = db.exec(
                    select(Account).where(Account.id == payment.account_id)
                ).first()
                if not account:
                    raise HTTPException(
                        status_code=404, detail="Payment method not found."
                    )
                db.add(
                    Payment(
                        date_received=payment.date_received,
                        reference_number=payment.reference_number,
                        amount=payment.amount,
                        notes=payment.notes,
                        account_name_snapshot=account.name,
                        account_id=account.id,
                        job_order=job_order,
                    )
                )
        if data.claiming_history:
            for claim in data.claiming_history:
                db.add(
                    ClaimingHistory(
                        date_claimed=claim.date_claimed,
                        name=claim.name,
                        pcs_claimed=claim.pcs_claimed,
                        job_order=job_order,
                        job_item=job_item,
                        claimed_item_id=job_item.item_id,
                    )
                )
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


def update_job_order(
    db: Session, jo_number: int, data: JobOrderCreate, current_user_id: uuid.UUID
):
    try:
        job_order = db.exec(
            select(JobOrder).where(JobOrder.jo_number == jo_number)
        ).first()
        if not job_order:
            raise HTTPException(status_code=404, detail="Job order not found")

        # Update basic fields
        job_order.date_received = data.date_received
        job_order.override_payment_status = data.override_payment_status
        job_order.updated_at = datetime.now(timezone.utc)
        job_order.updated_by_id = current_user_id

        # Customer lookup by name (same as create)
        if not data.customer_name:
            raise HTTPException(status_code=400, detail="Customer name is required.")
        customer = db.exec(
            select(Customer).where(Customer.name == data.customer_name)
        ).first()
        if not customer:
            assert data.customer_name
            assert data.customer_address
            assert data.customer_contact_no
            assert data.customer_email
            customer = Customer(
                name=data.customer_name,
                address=data.customer_address,
                contact_no=data.customer_contact_no,
                email=data.customer_email,
            )
            db.add(customer)
            db.flush()
        job_order.customer_id = customer.id
        db.add(job_order)
        db.flush()

        # 1. Delete everything first
        for existing_claim in job_order.claims:
            db.delete(existing_claim)
        db.flush()

        for existing_payment in job_order.payments:
            db.delete(existing_payment)
        db.flush()

        for existing_item in job_order.job_items:
            db.delete(existing_item)
        db.flush()

        # 2. Insert job items first
        for item in data.job_items:
            service_type = db.exec(
                select(Service).where(Service.name == item.service_name)
            ).first()
            if not service_type:
                raise HTTPException(status_code=404, detail="Service type not found")
            extra_type = None
            if item.extra_service_name:
                extra_type = db.exec(
                    select(ExtraService).where(
                        ExtraService.name == item.extra_service_name
                    )
                ).first()
                if not extra_type:
                    raise HTTPException(status_code=404, detail="Extra type not found")
            job_item = JobItem(
                jo_number=data.jo_number,
                item_id=item.item_id,
                description=item.description,
                height=item.height,
                width=item.width,
                size_unit=item.size_unit,
                quantity=item.quantity,
                job_status=item.job_status,
                due_date=item.due_date,
                discount=item.discount,
                job_order_id=job_order.id,
                service_type_id=service_type.id,
                extra_type_id=extra_type.id if extra_type else None,
            )
            db.add(job_item)
            db.flush()

        # 3. Insert claims using the map instead of querying
        if data.claims:
            for claim in data.claims:
                job_item = db.exec(
                    select(JobItem).where(JobItem.item_id == claim.claimed_item_id)
                ).first()
                if not job_item:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Job item ID {claim.claimed_item_id} not found",
                    )
                claim_item = ClaimingHistory(
                    date_claimed=claim.date_claimed,
                    name=claim.name,
                    pcs_claimed=claim.pcs_claimed,
                    job_order_id=job_order.id,
                    job_item_id=job_item.id,
                    claimed_item_id=job_item.item_id,
                )
                db.add(claim_item)

        # 4. Insert payments
        if data.payments:
            for payment in data.payments:
                paymentItem = Payment(
                    date_received=payment.date_received,
                    method=payment.method,
                    amount=payment.amount,
                    job_order_id=job_order.id,
                )
                db.add(paymentItem)
        db.flush()
        db.refresh(job_order)
        job_order.sync_computed_fields()
        db.commit()
        db.refresh(job_order)

        audit = AuditLog(
            action=f"Updated job order {job_order.jo_number}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()

        return job_order
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
    now = datetime.now(timezone.utc)
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
    now = datetime.now(timezone.utc)
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
    now = datetime.now(timezone.utc)
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
    now = datetime.now(timezone.utc)
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
    now = datetime.now(timezone.utc)
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
    now = datetime.now(timezone.utc)
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
