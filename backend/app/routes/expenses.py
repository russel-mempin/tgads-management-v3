from app.models import Expense, ExpenseBase, User
from typing import Annotated
from app.services.dependencies import get_current_active_user
from fastapi import APIRouter, Query, Depends
from sqlmodel import Session
from app.database import get_session
from app.crud.expense import get_all_expenses, create_expense, update_expense, archive_expense
import uuid


router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[Expense])
def read_all(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_expenses(db, offset=offset, limit=limit)

@router.post("/", response_model=Expense)
def create(data: ExpenseBase, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_expense(db, data, current_user.id)

@router.patch("/{expense_id}", response_model=Expense)
def update(expense_id: uuid.UUID, data: ExpenseBase, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_expense(db, expense_id, data, current_user.id)

@router.patch("/{expense_id}/archive")
def archive(expense_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return archive_expense(db, expense_id, current_user.id)