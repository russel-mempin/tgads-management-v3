import uuid

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from app.enums import ReviewEntityType
from app.models import ForReview, JobOrder, UnlinkedPayment
from app.schemas.for_review import (
    ForReviewDetails,
    JobOrderPublic,
    UnlinkedPaymentReviewData,
)


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


def get_for_review_details(db: Session, for_review_id: uuid.UUID) -> ForReviewDetails:
    for_review_item = db.exec(
        select(ForReview)
        .where(ForReview.id == for_review_id)
        .options(
            selectinload(ForReview.created_by),
            selectinload(ForReview.resolved_by),
        )
    ).first()
    if not for_review_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="For Review item not found."
        )
    if for_review_item.entity_type == ReviewEntityType.PAYMENT:
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

        entity_data = UnlinkedPaymentReviewData(
            id=entity.id,
            date_received=entity.date_received,
            reference_number=entity.reference_number,
            amount=entity.amount,
            customer_name=entity.customer_name,
            description=entity.description,
            account_id=entity.account_id,
            account_name=entity.account.name if entity.account else None,
        )
    elif for_review_item.entity_type == ReviewEntityType.JOB_ORDER:
        entity = db.exec(
            select(JobOrder).where(JobOrder.id == for_review_item.entity_id)
        ).first()
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job order not found."
            )
        entity_data = JobOrderPublic.model_validate(entity, from_attributes=True)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported review entity type: {for_review_item.entity_type}",
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
