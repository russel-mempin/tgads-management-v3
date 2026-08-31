import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import String, cast, func, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from app.enums import PaymentStatus, ReviewEntityType, TransactionSource
from app.models import (
    AccountTransaction,
    AuditLog,
    Customer,
    ForReview,
    JobItem,
    JobOrder,
    MiscSale,
    Payment,
    UnlinkedPayment,
)
from app.schemas.for_review import (
    ForReviewDetails,
    PossibleJobOrder,
    UnlinkedPaymentReviewData,
)
from app.schemas.job_order import (
    JobItemCreate,
    JobItemPublic,
    JobOrderPublic,
)
from app.utils.job_order import (
    build_job_item,
    build_job_item_extra,
    get_extra_service_data_by_id,
)


def _normalize_name(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.lower().split())


def _build_for_review_details(
    for_review_item: ForReview, entity_data: UnlinkedPaymentReviewData | JobOrderPublic
) -> ForReviewDetails:
    return ForReviewDetails(
        id=for_review_item.id,
        entity_type=for_review_item.entity_type,
        entity_id=for_review_item.entity_id,
        entity_reference=for_review_item.entity_reference,
        reason=for_review_item.reason,
        reason_category=for_review_item.reason_category,
        created_at=for_review_item.created_at,
        created_by_name=for_review_item.created_by_name,
        entity=entity_data,
    )


def _calculate_job_order_match(
    payment: UnlinkedPayment,
    job_order: JobOrder,
) -> tuple[int, list[str]]:

    score = 0
    reasons: list[str] = []

    payment_customer = _normalize_name(payment.customer_name)

    job_customer = _normalize_name(
        job_order.customer.name if job_order.customer else None
    )

    # Customer
    if payment_customer and job_customer and payment_customer == job_customer:
        score += 50
        reasons.append("Customer name matches")

    # Amount
    remaining = job_order.total_due - job_order.total_paid

    if payment.amount == remaining:
        score += 40
        reasons.append("Amount matches remaining balance")
    elif payment.amount <= remaining:
        score += 20
        reasons.append("Amount is within remaining balance")

    # Date
    if payment.date_received and job_order.date_received:
        days_difference = abs(
            (payment.date_received.date() - job_order.date_received.date()).days
        )

        if days_difference == 0:
            score += 15
            reasons.append("Same date")
        elif days_difference <= 3:
            score += 10
            reasons.append("Within 3 days")
        elif days_difference <= 7:
            score += 5
            reasons.append("Within 7 days")

    return score, reasons


def _get_possible_job_orders_for_payment(
    db: Session,
    payment: UnlinkedPayment,
    limit: int = 10,
) -> list[PossibleJobOrder]:

    query = (
        select(JobOrder)
        .where(
            col(JobOrder.voided_at).is_(None),
            JobOrder.payment_status != PaymentStatus.FULLY_PAID,
        )
        .options(
            selectinload(JobOrder.customer),  # type: ignore
            selectinload(JobOrder.job_items),  # type: ignore
            selectinload(JobOrder.payments),  # type: ignore
        )
    )

    job_orders = db.exec(query).all()

    matches: list[PossibleJobOrder] = []

    for job_order in job_orders:
        # Don't suggest JOs that have no outstanding balance.
        if job_order.balance <= 0:
            continue

        score, reasons = _calculate_job_order_match(
            payment,
            job_order,
        )

        if score <= 0:
            continue

        matches.append(
            PossibleJobOrder(
                id=job_order.id,
                jo_number=job_order.jo_number,
                job_items=[
                    JobItemPublic.model_validate(
                        item,
                        from_attributes=True,
                    )
                    for item in job_order.job_items
                ],
                customer_name=job_order.customer_name,
                date_received=job_order.date_received,
                total_due=job_order.total_due,
                total_paid=job_order.total_paid,
                remaining_balance=job_order.balance,
                match_score=score,
                match_reasons=reasons,
            )
        )

    matches.sort(
        key=lambda match: match.match_score,
        reverse=True,
    )

    return matches[:limit]


def get_all_for_review_items(
    db: Session, offset: int = 0, limit: int = 100
) -> list[ForReview]:
    return list(db.exec(select(ForReview).offset(offset).limit(limit)).all())


def get_count_of_for_reviews(db: Session) -> int:
    return db.exec(select(func.count()).select_from(ForReview)).one()


def get_payment_for_review_details(
    db: Session,
    entity_id: uuid.UUID,
) -> ForReviewDetails:
    for_review_item = db.exec(
        select(ForReview).where(ForReview.entity_id == entity_id)
    ).first()

    if not for_review_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="For Review item not found.",
        )

    if for_review_item.entity_type != ReviewEntityType.PAYMENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entity type should be Payment.",
        )

    entity = db.exec(
        select(UnlinkedPayment)
        .where(UnlinkedPayment.id == for_review_item.entity_id)
        .options(selectinload(UnlinkedPayment.account))  # type: ignore
    ).first()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unlinked payment not found.",
        )

    # Find possible Job Order matches
    possible_matches = _get_possible_job_orders_for_payment(
        db=db,
        payment=entity,
    )

    entity_data = UnlinkedPaymentReviewData(
        id=entity.id,
        date_received=entity.date_received,
        reference_number=entity.reference_number,
        amount=entity.amount,
        customer_name=entity.customer_name,
        description=entity.description,
        account_id=entity.account_id,
        account_name=entity.account.name if entity.account else None,
        possible_matches=possible_matches,
    )

    return _build_for_review_details(for_review_item, entity_data)


def find_possible_job_orders(
    db: Session,
    payment: UnlinkedPayment,
    search_value: str,
) -> list[PossibleJobOrder]:
    search_value = search_value.strip()

    query = (
        select(JobOrder)
        .join(Customer, isouter=True)
        .where(
            col(JobOrder.voided_at).is_(None),
            JobOrder.payment_status != PaymentStatus.FULLY_PAID,
            or_(
                cast(JobOrder.jo_number, String).ilike(f"%{search_value}%"),
                Customer.name.ilike(f"%{search_value}%"),  # type: ignore
            ),
        )
        .options(
            selectinload(JobOrder.customer),  # type: ignore
            selectinload(JobOrder.job_items),  # type: ignore
            selectinload(JobOrder.payments),  # type: ignore
        )
    )

    job_orders = db.exec(query).all()

    results = []

    for job_order in job_orders:
        score, reasons = _calculate_job_order_match(
            payment,
            job_order,
        )

        results.append(
            PossibleJobOrder(
                id=job_order.id,
                jo_number=job_order.jo_number,
                job_items=[
                    JobItemPublic.model_validate(
                        item,
                        from_attributes=True,
                    )
                    for item in job_order.job_items
                ],
                customer_name=(job_order.customer.name if job_order.customer else None),
                date_received=job_order.date_received,
                total_due=job_order.total_due,
                total_paid=job_order.total_paid,
                remaining_balance=(job_order.total_due - job_order.total_paid),
                match_score=score,
                match_reasons=reasons,
            )
        )

    results.sort(
        key=lambda result: result.match_score,
        reverse=True,
    )

    return results


def assign_payment_to_job_order(
    db: Session, entity_id: uuid.UUID, match_id: uuid.UUID, current_user_id: uuid.UUID
):
    try:
        job_order = db.exec(select(JobOrder).where(JobOrder.id == match_id)).first()
        if not job_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job Order not found."
            )
        unlinked_payment = db.exec(
            select(UnlinkedPayment).where(UnlinkedPayment.id == entity_id)
        ).first()
        if not unlinked_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unlinked Payment not found.",
            )
        account = unlinked_payment.account
        for_review_data = db.exec(
            select(ForReview).where(ForReview.entity_id == unlinked_payment.id)
        ).first()
        if not for_review_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="For Review data not found.",
            )
        payment = Payment(
            date_received=unlinked_payment.date_received,
            reference_number=unlinked_payment.reference_number,
            amount=unlinked_payment.amount,
            notes="Assigned from unlinked payments.",
            account_name_snapshot=account.name,
            job_order_id=job_order.id,
            account_id=account.id,
        )
        db.add(payment)
        db.delete(for_review_data)
        db.delete(unlinked_payment)
        db.flush()
        job_order.sync_computed_fields()
        db.add(
            AccountTransaction(
                account_id=payment.account_id,
                amount=payment.amount,
                source_type=TransactionSource.PAYMENT,
                source_id=payment.id,
            )
        )
        audit = AuditLog(
            action=(
                f"Assigned unlinked payment "
                f"{unlinked_payment.reference_number} "
                f"(₱{unlinked_payment.amount}) "
                f"to job order {job_order.jo_number}."
            ),
            user_id=current_user_id,
        )
        db.add(audit)
        db.commit()
        return {
            "message": f"Payment successfully assigned to JO-{job_order.jo_number}."
        }
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def assign_payment_to_misc_sale(
    db: Session, entity_id: uuid.UUID, current_user_id: uuid.UUID
):
    try:
        unlinked_payment = db.exec(
            select(UnlinkedPayment).where(UnlinkedPayment.id == entity_id)
        ).first()
        if not unlinked_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unlinked Payment not found.",
            )
        account = unlinked_payment.account
        for_review_data = db.exec(
            select(ForReview).where(ForReview.entity_id == unlinked_payment.id)
        ).first()
        if not for_review_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="For Review data not found.",
            )
        if not unlinked_payment.description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment description is required",
            )
        misc_sale = MiscSale(
            date=unlinked_payment.date_received,
            description=unlinked_payment.description,
            amount=unlinked_payment.amount,
            account_id=account.id,
        )
        db.add(misc_sale)
        db.flush()
        db.delete(for_review_data)
        db.delete(unlinked_payment)
        db.add(
            AccountTransaction(
                account_id=misc_sale.account_id,
                amount=misc_sale.amount,
                source_type=TransactionSource.MISC_SALE,
                source_id=misc_sale.id,
            )
        )
        audit = AuditLog(
            action=(
                f"Marked unlinked payment to Misc Sale Ref. No. "
                f"{unlinked_payment.reference_number} "
                f"(₱{unlinked_payment.amount}) "
            ),
            user_id=current_user_id,
        )
        db.add(audit)
        db.commit()
        return {"message": "Payment successfully marked as Misc Sale."}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def get_job_for_review_details(db: Session, entity_id: uuid.UUID) -> ForReviewDetails:
    for_review_item = db.exec(
        select(ForReview).where(ForReview.entity_id == entity_id)
    ).first()
    if not for_review_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="For Review item not found."
        )
    if for_review_item.entity_type != ReviewEntityType.JOB_ORDER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entity type should be Job Order.",
        )
    entity = db.exec(
        select(JobOrder).where(JobOrder.id == for_review_item.entity_id)
    ).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job order not found."
        )
    entity_data = JobOrderPublic.model_validate(entity, from_attributes=True)
    return _build_for_review_details(for_review_item, entity_data)


def update_whole_job_item(
    db: Session,
    job_order_id: uuid.UUID,
    job_item_id: uuid.UUID,
    data: JobItemCreate,
    current_user_id: uuid.UUID,
):
    try:
        job_item = db.exec(
            select(JobItem).where(
                JobItem.id == job_item_id, JobItem.job_order_id == job_order_id
            )
        ).first()
        if not job_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job order not found."
            )
        extra_services = []
        for extra in data.extras:
            extra_service = get_extra_service_data_by_id(db, extra.extra_service_id)
            extra_services.append((extra, extra_service))
        new_item = build_job_item(db, job_order_id, data, extra_services)
        # Replace all fields except the primary key
        for field in [
            "description",
            "discount_amount",
            "due_date",
            "extra_charge",
            "height",
            "item_id",
            "job_status",
            "notes",
            "quantity",
            "service_abbreviation_snapshot",
            "service_option_name_snapshot",
            "service_name_snapshot",
            "size_unit",
            "subtotal",
            "unit_price",
            "width",
            "service_id",
            "service_option_id",
        ]:
            setattr(job_item, field, getattr(new_item, field))
        for extra in job_item.extras:
            db.delete(extra)
        db.flush()
        for extra, extra_service in extra_services:
            db.add(build_job_item_extra(job_item.id, extra, extra_service))
        db.flush()
        job_order = job_item.job_order
        job_order.sync_computed_fields()

        audit = AuditLog(
            action=f"Updated job item {job_item.item_id}", user_id=current_user_id
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


def void_job_order(
    db: Session,
    job_order_id: uuid.UUID,
    reason: str,
    current_user_id: uuid.UUID,
):
    try:
        job_order = db.exec(select(JobOrder).where(JobOrder.id == job_order_id)).first()

        if not job_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job order not found.",
            )

        if job_order.voided_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job order is already voided.",
            )

        for_review = db.exec(
            select(ForReview).where(
                ForReview.entity_type == ReviewEntityType.JOB_ORDER,
                ForReview.entity_id == job_order_id,
            )
        ).first()

        job_order.voided_at = datetime.now(UTC)
        job_order.void_reason = reason

        db.add(
            AuditLog(
                action=f"Voided job order {job_order.jo_number}",
                user_id=current_user_id,
            )
        )

        if for_review:
            db.delete(for_review)

        db.commit()
        db.refresh(job_order)

        return "Job Order voided."

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
