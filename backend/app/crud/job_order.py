from sqlmodel import Session, select, col
from sqlalchemy import or_, cast, String, func
from app.models import (
    JobOrder,
    JobItem,
    ServiceType,
    Customer,
    ExtraType,
    Payment,
    ClaimingHistory,
    AuditLog,
)
from fastapi import HTTPException
from app.utils.utils import compute_unit_price
from app.schemas.job_order import JobOrderCreate
from app.enums import SizeUnit, PaymentStatus, JobStatus
import uuid
from datetime import datetime, timedelta, timezone


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
        query = query.where(JobOrder.is_active == True)

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
        query = query.where(JobOrder.is_active == True)
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


def get_job_order(db: Session, jo_number: int) -> JobOrder:
    job_order = db.exec(select(JobOrder).where(JobOrder.jo_number == jo_number)).first()
    if not job_order:
        raise HTTPException(
            status_code=404,
            detail=f"Job order with JO number of {jo_number} not found.",
        )
    return job_order


def get_price(
    db: Session, height: float, width: float, service_name: str, size_unit: SizeUnit
) -> float:
    service = db.exec(
        select(ServiceType).where(ServiceType.name == service_name)
    ).first()

    if service is None:
        raise HTTPException(status_code=404, detail="Service type not found")

    return compute_unit_price(height, width, service, size_unit)


def create_job_order(db: Session, data: JobOrderCreate, current_user_id: uuid.UUID):
    try:
        if data.customer_id:
            customer = db.exec(
                select(Customer).where(Customer.id == data.customer_id)
            ).first()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
        else:
            if not all(
                [
                    data.customer_name,
                    data.customer_address,
                    data.customer_contact_no,
                    data.customer_email,
                ]
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Name, address, email, and contact number are required for new customers. You can also put N/A if not applicable for walk-in customers.",
                )

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
        job_order = JobOrder(
            jo_number=data.jo_number,
            date_received=data.date_received,
            customer_id=customer.id,
        )
        db.add(job_order)
        db.flush()

        for item in data.job_items:
            service_type = db.exec(
                select(ServiceType).where(ServiceType.id == item.service_type_id)
            ).first()
            if not service_type:
                raise HTTPException(status_code=404, detail="Service type not found")
            extra_type = None
            if item.extra_type_id:
                extra_type = db.exec(
                    select(ExtraType).where(ExtraType.id == item.extra_type_id)
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
            job_order.job_items.append(job_item)
            db.add(job_item)
            db.flush()
        if data.payments:
            for payment in data.payments:
                paymentItem = Payment(
                    date_received=payment.date_received,
                    method=payment.method,
                    amount=payment.amount,
                    job_order_id=job_order.id,
                )
                job_order.payments.append(paymentItem)
                db.add(paymentItem)
        if data.claims:
            for claim in data.claims:
                job_item = db.exec(
                    select(JobItem).where(JobItem.item_id == claim.claimed_item_id)
                ).first()
                if not job_item:
                    raise HTTPException(status_code=404, detail="Job Item ID not found")
                claimItem = ClaimingHistory(
                    date_claimed=claim.date_claimed,
                    name=claim.name,
                    pcs_claimed=claim.pcs_claimed,
                    job_order_id=job_order.id,
                    job_item_id=job_item.id,
                    claimed_item_id=job_item.item_id,
                )
                job_order.claims.append(claimItem)
                db.add(claimItem)
        job_order.sync_computed_fields()
        db.add(job_order)
        db.commit()
        db.refresh(job_order)

        audit = AuditLog(
            action=f"Created job order {job_order.jo_number}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()

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
            action=f"Archived job order {job_order.jo_number}", user_id=current_user_id
        )
        db.add(audit)

        db.commit()
        db.refresh(job_order)
        return "Job order archived."
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

        # Update basic job order fields
        job_order.date_received = data.date_received
        job_order.override_payment_status = data.override_payment_status

        # If updated customer is new, there's name and other info. If old, only ID.
        if data.customer_id:
            customer = db.exec(
                select(Customer).where(Customer.id == data.customer_id)
            ).first()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            job_order.customer_id = customer.id
        else:
            if not all(
                [
                    data.customer_name,
                    data.customer_address,
                    data.customer_contact_no,
                    data.customer_email,
                ]
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Name, address, email, and contact number are required for new customers. You can also put N/A if not applicable for walk-in customers.",
                )
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
                select(ServiceType).where(ServiceType.id == item.service_type_id)
            ).first()
            if not service_type:
                raise HTTPException(status_code=404, detail="Service type not found")
            extra_type = None
            if item.extra_type_id:
                extra_type = db.exec(
                    select(ExtraType).where(ExtraType.id == item.extra_type_id)
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
        fresh_payments = db.exec(
            select(Payment).where(Payment.job_order_id == job_order.id)
        ).all()
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


def get_job_order_kpis(db: Session) -> dict:
    # Outstanding balance — sum of (total_due - total_paid) for unpaid/partial orders
    job_orders = db.exec(
        select(JobOrder).where(
            JobOrder.is_active == True,
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
        .where(
            JobOrder.is_active == True, JobOrder.payment_status == PaymentStatus.UNPAID
        )
    ).one()

    # Count of overdue jobs — job items past due_date and not released/cancelled
    now = datetime.now(timezone.utc)
    overdue_count = db.exec(
    select(func.count()).select_from(JobItem).where(
        JobItem.due_date < now,
        col(JobItem.job_status).not_in([JobStatus.RELEASED, JobStatus.CANCELLED])
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
