import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.crud.for_review import (
    assign_payment_to_job_order,
    assign_payment_to_misc_sale,
    find_possible_job_orders,
    get_all_for_review_items,
    get_count_of_for_reviews,
    get_job_for_review_details,
    get_job_item_with_job_order,
    get_payment_for_review_details,
    mark_job_as_resolved,
    update_whole_job_item,
    void_job_order,
)
from app.database import get_session
from app.models import UnlinkedPayment, User
from app.schemas.for_review import (
    ForReviewDetails,
    ForReviewPublic,
    PossibleJobOrder,
)
from app.schemas.job_order import JobItemCreate
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/for-reviews", tags=["for-reviews"], dependencies=[Depends(get_current_active_user)])

# TODO: Change all entity_id to their entity name_id
@router.get("/", response_model=list[ForReviewPublic])
def read_all_for_review_items(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_for_review_items(db, offset=offset, limit=limit)


@router.get("/count", response_model=int)
def read_count_of_for_review_items(db: Session = Depends(get_session)):
    return get_count_of_for_reviews(db)


@router.get("/payments/{payment_id}", response_model=ForReviewDetails)
def read_payment_for_review_details(payment_id: uuid.UUID, db: Session = Depends(get_session)):
    return get_payment_for_review_details(db, payment_id)


@router.get("/payments/{payment_id}/possible-job-orders/search", response_model=list[PossibleJobOrder])
def search_possible_job_orders(payment_id: uuid.UUID, search_value: str, db: Session = Depends(get_session)):
    payment = db.get(UnlinkedPayment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unlinked Payment not found."
        )
    return find_possible_job_orders(db, payment, search_value)


@router.post("/payments/{payment_id}/job-assign")
def create_payment_data_to_job(payment_id: uuid.UUID, match_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return assign_payment_to_job_order(db, payment_id, match_id, current_user.id)


@router.post("/payments/{payment_id}/misc-assign")
def create_payment_data_to_misc(payment_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return assign_payment_to_misc_sale(db, payment_id, current_user.id)


@router.get("/job-orders/{job_order_id}", response_model=ForReviewDetails)
def read_job_for_review_details(job_order_id: uuid.UUID, db: Session = Depends(get_session)):
    return get_job_for_review_details(db, job_order_id)


@router.put("/job-orders/{job_order_id}/job-items/{job_item_id}")
def update_job_item(job_order_id: uuid.UUID, job_item_id: uuid.UUID, data: JobItemCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_whole_job_item(db, job_order_id, job_item_id, data, current_user.id)


@router.patch("/job-orders/{job_order_id}/void")
def void_job_order_and_delete_review(job_order_id: uuid.UUID, reason: str, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return void_job_order(db, job_order_id, reason, current_user.id)


@router.get("/job-items/{job_item_id}")
def get_job_item_review_details(job_item_id: uuid.UUID, db: Session = Depends(get_session)):
    return get_job_item_with_job_order(db, job_item_id)


@router.patch("/job-orders/{job_order_id}/resolve")
def resolve_job(job_order_id: uuid.UUID, db: Session = Depends(get_session)):
    return mark_job_as_resolved(db, job_order_id)