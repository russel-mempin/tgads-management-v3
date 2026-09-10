import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from app.enums import ExpenseCategory, ExpensePeriod, TransactionSource
from app.models import Account, AccountTransaction, AuditLog, Expense
from app.schemas.expense import ExpenseCreate, ExpenseList, ExpenseSummary
from app.utils.utils import MANILA


def _get_expense_date_range(period: ExpensePeriod):
    now = datetime.now(MANILA)

    if period == ExpensePeriod.TODAY:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif period == ExpensePeriod.THIS_WEEK:
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=7)
    elif period == ExpensePeriod.THIS_MONTH:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (
            start.replace(year=start.year + 1, month=1)
            if start.month == 12
            else start.replace(month=start.month + 1)
        )
    elif period == ExpensePeriod.LAST_MONTH:
        end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start = (
            end.replace(year=end.year - 1, month=12)
            if end.month == 1
            else end.replace(month=end.month - 1)
        )
    elif period == ExpensePeriod.THIS_YEAR:
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(year=start.year + 1)
    else:
        return None, None

    return start, end


def get_all_expenses(
    db: Session,
    period: ExpensePeriod = ExpensePeriod.ALL,
    include_archived: bool = False,
    category: ExpenseCategory | None = None,
    search: str | None = None,
    offset: int = 0,
    limit: int = 100,
) -> ExpenseList:
    period_filters = []
    table_filters = []

    if not include_archived:
        table_filters.append(Expense.is_archived == False)

    start, end = _get_expense_date_range(period)
    if start and end:
        period_filters.extend(
            [
                Expense.date >= start,
                Expense.date < end,
            ]
        )

    # Summary — period only
    summary_statement = select(
        func.coalesce(func.sum(Expense.amount), 0),
        func.count(Expense.id),
    ).where(*period_filters)
    total, count = db.exec(summary_statement).one()
    
    largest_statement = (
        select(Expense)
        .where(*period_filters)
        .order_by(Expense.amount.desc())
        .limit(1)
    )
    largest = db.exec(largest_statement).first()

    # Table — period + filters
    table_filters.extend(period_filters)

    if category:
        table_filters.append(Expense.category == category)

    if search:
        table_filters.append(Expense.description.ilike(f"%{search}%"))

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
    )


def count_all_expenses(db: Session) -> int:
    return db.exec(select(func.count()).select_from(Expense)).one()


def get_today_expenses(db: Session) -> list[Expense]:
    start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    return list(
        db.exec(
            select(Expense).where(
                Expense.is_archived == False,
                Expense.date >= start,
                Expense.date < end,
            )
        ).all()
    )


def create_expense(db: Session, data: ExpenseCreate, current_user_id: uuid.UUID):
    try:
        account = db.exec(select(Account).where(Account.id == data.fund_source)).first()
        if not account:
            raise ValueError("Fund source not found in database")

        print(data.date)
        print(repr(data.date))
        print(data.date.tzinfo)

        expense = Expense(
            date=data.date,
            category=data.category,
            amount=data.amount,
            description=data.description,
            account_id=account.id,
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)

        new_balance = account.current_balance - expense.amount
        account.current_balance = new_balance
        db.add(account)
        transaction = AccountTransaction(
            account_id=account.id,
            date=data.date,
            description=data.description,
            amount=expense.amount,
            running_balance=new_balance,
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
    db: Session, expense_id: uuid.UUID, data: ExpenseCreate, current_user_id: uuid.UUID
):
    try:
        print(expense_id)
        expense = db.exec(select(Expense).where(Expense.id == expense_id)).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found.")

        # Reverse the old transaction
        old_account = db.exec(
            select(Account).where(Account.id == expense.account_id)
        ).first()
        if old_account:
            old_account.current_balance += expense.amount  # add back the old amount
            db.add(old_account)

            reversal = AccountTransaction(
                account_id=old_account.id,
                date=datetime.now(UTC),
                description=f"Reversal: {expense.description}",
                amount=expense.amount,  # positive = money back
                running_balance=old_account.current_balance,
                source_type=TransactionSource.EXPENSE_REVERSAL,
                source_id=expense.id,
            )
            db.add(reversal)

        # Update expense fields
        expense.date = data.date
        expense.category = data.category
        expense.amount = data.amount
        expense.description = data.description
        expense.account_id = data.fund_source
        db.add(expense)
        db.flush()

        # Create new transaction with updated values
        new_account = db.exec(
            select(Account).where(Account.id == data.fund_source)
        ).first()
        if not new_account:
            raise HTTPException(status_code=404, detail="Account not found.")

        new_account.current_balance -= data.amount
        db.add(new_account)

        new_transaction = AccountTransaction(
            account_id=new_account.id,
            date=data.date,
            description=data.description,
            amount=-data.amount,  # negative = money out
            running_balance=new_account.current_balance,
            source_type=TransactionSource.EXPENSE,
            source_id=expense.id,
        )
        db.add(new_transaction)

        db.commit()
        db.refresh(expense)

        audit = AuditLog(
            action=f"Updated expense: {expense.description}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()

        return expense
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def archive_expense(db: Session, expense_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        expense = db.exec(select(Expense).where(Expense.id == expense_id)).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        # Reverse the transaction
        account = db.exec(
            select(Account).where(Account.id == expense.account_id)
        ).first()
        if account:
            account.current_balance += expense.amount  # add back the amount
            db.add(account)

            reversal = AccountTransaction(
                account_id=account.id,
                date=datetime.now(UTC),
                description=f"Reversal (archived): {expense.description}",
                amount=expense.amount,  # positive = money back
                running_balance=account.current_balance,
                source_type=TransactionSource.EXPENSE_REVERSAL,
                source_id=expense.id,
            )
            db.add(reversal)

        expense.is_archived = True
        db.add(expense)

        audit = AuditLog(
            action=f"Archived expense: {expense.description}", user_id=current_user_id
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
