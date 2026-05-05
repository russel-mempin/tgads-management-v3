from fastapi import APIRouter, Query, Depends
from app.schemas.job_order import JobOrderPublic
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.crud.job_order import get_all_job_orders, get_price, create_job_order
from app.schemas.job_order import JobOrderCreate


router = APIRouter(prefix="/job-orders", tags=["job-orders"])


@router.get("/", response_model=list[JobOrderPublic])
def read_all(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_job_orders(db, offset=offset, limit=limit)

@router.get("/compute-unit-price", response_model=float)
def compute_unit_price(
    height: float,
    width: float,
    service_name: str,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    db: Session = Depends(get_session)
):
    return get_price(db, height=height, width=width, service_name=service_name)

@router.post("/", response_model=JobOrderPublic)
def create(data: JobOrderCreate, db: Session = Depends(get_session)):
    return create_job_order(db, data)