from fastapi import APIRouter, Query, Depends
from app.schemas.job_order import JobOrderPublic
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.crud.job_order import get_all_job_orders, get_job_order, get_price, create_job_order
from app.schemas.job_order import JobOrderCreate
from app.services.dependencies import get_current_active_user
from app.models import User


router = APIRouter(prefix="/job-orders", tags=["job-orders"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[JobOrderPublic])
def read_all(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_job_orders(db, offset=offset, limit=limit)

@router.get("/compute-unit-price", response_model=float)
def compute_unit_price(
    height: float,
    width: float,
    service_name: str,
    db: Session = Depends(get_session)
):
    return get_price(db, height=height, width=width, service_name=service_name)

@router.get("/{jo_number}", response_model=JobOrderPublic)
def read_job_order(jo_number: str, db: Session = Depends(get_session)):
    return get_job_order(db, jo_number)

@router.post("/", response_model=JobOrderPublic)
def create(data: JobOrderCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_job_order(db, data, current_user.id)