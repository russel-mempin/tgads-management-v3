import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.crud.expense import (
    archive_expense,
    count_all_expenses,
    create_expense,
    get_all_expenses,
    get_today_expenses,
    update_expense,
)
from app.database import get_session
from app.enums import ExpenseCategory, ExpensePeriod, UserRoles
from app.models import User
from app.schemas.expense import ExpenseCreate, ExpenseList, ExpensePublic
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=ExpenseList)
def read_all(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    db: Session = Depends(get_session),
    include_archived: bool = False,
    period: ExpensePeriod = ExpensePeriod.ALL,
    category: ExpenseCategory | None = None,
    search: str | None = None,
    current_user: User = Depends(get_current_active_user),
):
    # Non-owners can only view today's expenses
    if current_user.role != UserRoles.OWNER:
        if period != ExpensePeriod.TODAY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non-owner users can only access today's expenses.",
            )

        # Non-owners cannot access archived expenses
        if include_archived:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can access archived expenses.",
            )

    return get_all_expenses(
        db,
        period=period,
        include_archived=include_archived,
        category=category,
        search=search,
        offset=offset,
        limit=limit,
    )


@router.get("/count", response_model=int)
def read_count_of_expenses(db: Session = Depends(get_session)):
    return count_all_expenses(db)


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