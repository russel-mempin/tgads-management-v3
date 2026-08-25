import uuid

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from app.enums import PaymentStatus, ReviewEntityType
from app.models import ForReview, JobOrder, UnlinkedPayment
from app.schemas.for_review import (
    ForReviewDetails,
    JobOrderPublic,
    PossibleJobOrder,
    UnlinkedPaymentReviewData,
)


def _normalize_name(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.lower().split())


def _build_for_review_details():
    print("Do something")


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


def get_all_for_review_items(
    db: Session, offset: int = 0, limit: int = 100
) -> list[ForReview]:
    return list(db.exec(select(ForReview).offset(offset).limit(limit)).all())


def get_count_of_for_reviews(db: Session) -> int:
    return db.exec(
        select(func.count())
        .select_from(ForReview)
        .where(col(ForReview.resolved_at).is_(None))
    ).one()


def get_job_for_review_details(db: Session, entity_id: uuid.UUID) -> ForReviewDetails:
    for_review_item = db.exec(
        select(ForReview)
        .where(ForReview.entity_id == entity_id)
        .options(
            selectinload(ForReview.created_by),
            selectinload(ForReview.resolved_by),
        )
    ).first()
    if not for_review_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="For Review item not found."
        )
    if not for_review_item.entity_type == ReviewEntityType.JOB_ORDER:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
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
    return ForReviewDetails(
        id=for_review_item.id,
        entity_type=for_review_item.entity_type,
        entity_id=for_review_item.entity_id,
        entity_reference=for_review_item.entity_reference,
        reason=for_review_item.reason,
        reason_category=for_review_item.reason_category,
        resolution_note=for_review_item.resolution_note,
        created_at=for_review_item.created_at,
        created_by_name=for_review_item.created_by_name,
        resolved_at=for_review_item.resolved_at,
        resolved_by_id=for_review_item.resolved_by_id,
        resolved_by_name=for_review_item.resolved_by_name,
        entity=entity_data,
    )


def get_possible_job_orders_for_payment(
    db: Session,
    payment: UnlinkedPayment,
    limit: int = 10,
) -> list[PossibleJobOrder]:

    query = (
        select(JobOrder)
        .where(
            JobOrder.is_active,
            JobOrder.payment_status != PaymentStatus.FULLY_PAID,
        )
        .options(
            selectinload(JobOrder.customer),
            selectinload(JobOrder.job_items),
            selectinload(JobOrder.payments),
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
                job_items=job_order.job_items,
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


def get_payment_for_review_details(
    db: Session,
    entity_id: uuid.UUID,
) -> ForReviewDetails:
    for_review_item = db.exec(
        select(ForReview)
        .where(ForReview.entity_id == entity_id)
        .options(
            selectinload(ForReview.created_by),
            selectinload(ForReview.resolved_by),
        )
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
        .options(selectinload(UnlinkedPayment.account))
    ).first()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unlinked payment not found.",
        )

    # Find possible Job Order matches
    possible_matches = get_possible_job_orders_for_payment(
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

    return ForReviewDetails(
        id=for_review_item.id,
        entity_type=for_review_item.entity_type,
        entity_id=for_review_item.entity_id,
        entity_reference=for_review_item.entity_reference,
        reason=for_review_item.reason,
        reason_category=for_review_item.reason_category,
        resolution_note=for_review_item.resolution_note,
        created_at=for_review_item.created_at,
        created_by_name=for_review_item.created_by_name,
        resolved_at=for_review_item.resolved_at,
        resolved_by_id=for_review_item.resolved_by_id,
        resolved_by_name=for_review_item.resolved_by_name,
        entity=entity_data,
    )