from app.models import Expense, ExpenseBase
from typing import Annotated
from app.services.dependencies import get_current_active_user
from fastapi import APIRouter, Query, Depends
from sqlmodel import Session
from app.database import get_session
from app.crud.expense import get_all_expenses


router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[Expense])
def read_all(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_expenses(db, offset=offset, limit=limit)
