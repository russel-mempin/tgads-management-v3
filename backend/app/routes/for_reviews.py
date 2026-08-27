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
    get_payment_for_review_details,
)
from app.database import get_session
from app.models import UnlinkedPayment, User
from app.schemas.for_review import (
    ForReviewDetails,
    ForReviewPublic,
    PossibleJobOrder,
)
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/for-reviews", tags=["for-reviews"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[ForReviewPublic])
def read_all_for_review_items(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_for_review_items(db, offset=offset, limit=limit)


@router.get("/count", response_model=int)
def read_count_of_for_review_items(db: Session = Depends(get_session)):
    return get_count_of_for_reviews(db)


@router.get("/job-orders/{entity_id}", response_model=ForReviewDetails)
def read_job_for_review_details(entity_id: uuid.UUID, db: Session = Depends(get_session)):
    return get_job_for_review_details(db, entity_id)


@router.get("/payments/{entity_id}", response_model=ForReviewDetails)
def read_payment_for_review_details(entity_id: uuid.UUID, db: Session = Depends(get_session)):
    return get_payment_for_review_details(db, entity_id)


@router.get("/payments/{entity_id}/possible-job-orders/search", response_model=list[PossibleJobOrder])
def search_possible_job_orders(entity_id: uuid.UUID, search_value: str, db: Session = Depends(get_session)):
    payment = db.get(UnlinkedPayment, entity_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unlinked Payment not found."
        )
    return find_possible_job_orders(db, payment, search_value)


@router.post("/payments/{entity_id}/job-assign")
def create_payment_data_to_job(entity_id: uuid.UUID, match_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return assign_payment_to_job_order(db, entity_id, match_id, current_user.id)


@router.post("/payments/{entity_id}/misc-assign")
def create_payment_data_to_misc(entity_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return assign_payment_to_misc_sale(db, entity_id, current_user.id)