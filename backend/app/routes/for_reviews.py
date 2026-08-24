import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.for_review import (
    get_all_for_review_items,
    get_count_of_for_reviews,
    get_job_for_review_details,
    get_payment_for_review_details,
)
from app.database import get_session
from app.schemas.for_review import ForReviewDetails, ForReviewPublic
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