from app.models import ExpenseBase, User
from app.enums import UserRoles
from app.schemas.expense import ExpensePublic, ExpenseCreate
from typing import Annotated
from app.services.dependencies import get_current_active_user, require_role
from fastapi import APIRouter, Query, Depends
from sqlmodel import Session
from app.database import get_session
from app.crud.expense import get_all_expenses, get_today_expenses, create_expense, update_expense, archive_expense
import uuid


router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[ExpensePublic])
def read_all(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_role(UserRoles.OWNER)),
):
    return get_all_expenses(db, offset=offset, limit=limit)

@router.get("/today", response_model=list[ExpensePublic])
def read_all_daily(
    db: Session = Depends(get_session)
):
    return get_today_expenses(db)

@router.post("/", response_model=ExpensePublic)
def create(data: ExpenseCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_expense(db, data, current_user.id)

@router.patch("/{expense_id}", response_model=ExpensePublic)
def update(expense_id: uuid.UUID, data: ExpenseCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_expense(db, expense_id, data, current_user.id)

@router.patch("/{expense_id}/archive")
def archive(expense_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return archive_expense(db, expense_id, current_user.id)