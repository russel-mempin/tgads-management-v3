import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlmodel import Session, select

from app.enums import (
    DatePeriod,
    ExpenseCategory,
    ReasonCategory,
    ReviewEntityType,
    TransactionSource,
    UserRoles,
)
from app.models import Account, AccountTransaction, AuditLog, Expense, ForReview, User
from app.schemas.expense import (
    ExpenseByCategory,
    ExpenseCreate,
    ExpenseList,
    ExpenseSummary,
    ExpenseUpdate,
)
from app.utils.utils import get_date_range


def get_all_expenses(
    db: Session,
    period: DatePeriod = DatePeriod.ALL,
    include_archived: bool = False,
    category: ExpenseCategory | None = None,
    search: str | None = None,
    offset: int = 0,
    limit: int = 100,
) -> ExpenseList:
    base_filters = []
    period_filters = []

    if not include_archived:
        base_filters.append(Expense.is_archived == False)

    start, end = get_date_range(period)
    if start and end:
        period_filters.extend([
            Expense.date >= start,
            Expense.date < end,
        ])

    summary_filters = [*base_filters, *period_filters]

    # Summary — period only
    summary_statement = select(
        func.coalesce(func.sum(Expense.amount), 0),
        func.count(Expense.id),
    ).where(*summary_filters)
    total, count = db.exec(summary_statement).one()
    
    largest_statement = (
        select(Expense)
        .where(*period_filters)
        .order_by(Expense.amount.desc())
        .limit(1)
    )
    largest = db.exec(largest_statement).first()
    
    category_statement = (
        select(
            Expense.category,
            func.sum(Expense.amount).label("amount"),
        )
        .where(*summary_filters)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    )

    expense_by_category = [
        ExpenseByCategory(
            category=category,
            amount=amount,
        )
        for category, amount in db.exec(category_statement).all()
    ]

    # Table — period + filters
    table_filters = [*summary_filters]
    if category:
        table_filters.append(Expense.category == category)

    if search:
        table_filters.append(
            Expense.description.ilike(f"%{search}%")
        )

    # Pagination count
    table_count_statement = select(func.count(Expense.id)).where(*table_filters)

    table_count = db.exec(table_count_statement).one()

    # Table data
    expense_statement = (
        select(Expense)
        .where(*table_filters)
        .order_by(Expense.date.desc())
        .offset(offset)
        .limit(limit)
    )

    expenses = list(db.exec(expense_statement).all())

    return ExpenseList(
        items=expenses,
        total_items=table_count,
        summary=ExpenseSummary(
            total=total,
            count=count,
            largest=largest,
        ),
        expense_by_category=expense_by_category
    )


def count_all_expenses(db: Session) -> int:
    return db.exec(select(func.count()).select_from(Expense)).one()


def create_expense(db: Session, data: ExpenseCreate, current_user_id: uuid.UUID):
    try:
        account = db.exec(select(Account).where(Account.id == data.account_id)).first()
        if not account:
            raise ValueError("Fund source not found in database")

        expense = Expense(
            date=data.date,
            category=data.category,
            amount=data.amount,
            description=data.description,
            account_id=account.id,
            account_name_snapshot=account.name,
            created_by_id=current_user_id
        )
        db.add(expense)
        db.flush()

        transaction = AccountTransaction(
            account_id=account.id,
            date=data.date,
            description=data.description,
            amount=expense.amount,
            source_type=TransactionSource.EXPENSE,
            source_id=expense.id,
        )
        db.add(transaction)
        audit = AuditLog(
            action=f"Created expense {expense.description}", user_id=current_user_id
        )   
        db.add(audit)
        db.commit()

        return expense
    except Exception:
        db.rollback()
        raise


def update_expense(
    db: Session, expense_id: uuid.UUID, data: ExpenseUpdate, current_user_id: uuid.UUID
):
    try:
        expense = db.exec(select(Expense).where(Expense.id == expense_id)).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found.")

        old_amount = expense.amount
        old_date = expense.date
        old_account = expense.account

        update_data = data.model_dump(exclude_unset=True)
        old_data = {}
        new_data = {}

        for field, value in update_data.items():
            old_value = getattr(expense, field)

            if old_value != value:
                old_data[field] = jsonable_encoder(old_value)
                new_data[field] = jsonable_encoder(value)
                setattr(expense, field, value)

        if not new_data:
            return "No changes detected."
        expense.updated_by_id = current_user_id

        if "account_id" in new_data:
            new_account = db.get(Account, expense.account_id)
            if not new_account:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fund source account not found.")
            expense.account_name_snapshot = new_account.name
        
        if any(field in new_data for field in ("amount", "date", "account_id")):
            db.add(
                AccountTransaction(
                    date=old_date,
                    amount=-old_amount,
                    source_type=TransactionSource.REVERSAL,
                    source_id=expense.id,
                    account=old_account,
                    description=f"Reversal of expense: {expense.description}"
                )
            )
            db.add(
                AccountTransaction(
                    date=expense.date,
                    amount=expense.amount,
                    source_type=TransactionSource.EXPENSE,
                    source_id=expense.id,
                    account=expense.account,
                    description=f"Expense: {expense.description}"
                )
            )
        db.add(expense)
        audit = AuditLog(
            action=f"Updated expense: {expense.description}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        return "Expense data successfully updated."
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def archive_expense(db: Session, expense_id: uuid.UUID, current_user: User):
    try:
        expense = db.exec(select(Expense).where(Expense.id == expense_id)).first()
        if not expense:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        if expense.created_by_id != current_user.id and current_user.role != UserRoles.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to archive this expense.",
            )
        if expense.is_archived:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expense is already archived.",
            )
        expense.is_archived = True
        db.add(expense)

        if current_user.role != UserRoles.OWNER:
            db.add(
                ForReview(
                    entity_type=ReviewEntityType.EXPENSE,
                    entity_id=expense.id,
                    entity_reference=expense.description,
                    reason_category=ReasonCategory.EDIT_REQUIRES_APPROVAL,
                    old_data={"is_archived": False},
                    new_data={"is_archived": True},
                    reason="Expense archived by non-owner",
                    created_by_id=current_user.id,
                )
            )
        # Reverse the transaction
        account = db.exec(
            select(Account).where(Account.id == expense.account_id)
        ).first()
        if account:
            db.add(AccountTransaction(
                date=datetime.now(UTC),
                amount=expense.amount,
                source_type=TransactionSource.REVERSAL,
                source_id=expense.id,
                account=account,
                description=f"Expense Reversal: {expense.description}",
            ))

        audit = AuditLog(
            action=f"Archived expense: {expense.description}", user_id=current_user.id
        )
        db.add(audit)
        db.commit()
        db.refresh(expense)
        return "Expense archived."
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
