from fastapi import APIRouter, Query, Depends
from typing import Annotated
from app.services.dependencies import get_current_active_user
from sqlmodel import Session
from app.database import get_session
from app.schemas.for_review import ForReviewPublic
from app.crud.for_review import get_all_for_review_items


router = APIRouter(prefix="/for-reviews", tags=["for-reviews"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[ForReviewPublic])
def read_all_for_review_items(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_for_review_items(db, offset=offset, limit=limit)