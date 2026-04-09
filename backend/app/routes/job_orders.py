from fastapi import APIRouter, Query, Depends
from app.schemas.job_order import JobOrderPublic
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.crud.job_order import get_all_job_orders


router = APIRouter(prefix="/job-orders", tags=["job-orders"])


@router.get("/", response_model=list[JobOrderPublic])
def read_all(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_job_orders(db, offset=offset, limit=limit)