from sqlmodel import Session, select
from app.models import (
    JobOrder,
    JobItem,
    ServiceType,
    Customer,
    ExtraType,
    Payment,
    ClaimingHistory,
)
from fastapi import HTTPException
from app.utils.utils import compute_unit_price
from app.schemas.job_order import JobOrderCreate


def get_all_job_orders(
    db: Session, offset: int = 0, limit: int = 100
) -> list[JobOrder]:
    job_orders = list(db.exec(select(JobOrder).offset(offset).limit(limit)).all())
    return job_orders


def get_price(db: Session, height: float, width: float, service_name: str) -> float:
    service = db.exec(
        select(ServiceType).where(ServiceType.name == service_name)
    ).first()

    if service is None:
        raise HTTPException(status_code=404, detail="Service type not found")

    return compute_unit_price(height, width, service)


def create_job_order(db: Session, data: JobOrderCreate):
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
                paper_size=item.paper_size,
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
                    select(JobItem).where(JobItem.item_id == claim.job_item_id)
                ).first()
                if not job_item:
                    raise HTTPException(status_code=404, detail="Job Item ID not found")
                claimItem = ClaimingHistory(
                    date_claimed=claim.date_claimed,
                    name=claim.name,
                    pcs_claimed=claim.pcs_claimed,
                    job_order_id=job_order.id,
                    job_item_id=job_item.id,
                )
                job_order.claims.append(claimItem)
                db.add(claimItem)
        db.add(job_order)
        db.commit()
        db.refresh(job_order)

        return job_order
    except Exception:
        db.rollback()
        raise
