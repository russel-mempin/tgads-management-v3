from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.crud.performance import get_monthly_performance_list
from app.database import get_session
from app.schemas.performance import MonthlyPerformance, MonthlyPerformanceBase
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/performances", tags=["performances"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[MonthlyPerformanceBase])
def read_monthly_performance_list(year: int, db: Session = Depends(get_session)):
    return get_monthly_performance_list(db, year)


@router.get("/{year}/{month}", response_model=MonthlyPerformance)
def read_month_performance(year: int, month: int, db: Session = Depends(get_session)):
    pass