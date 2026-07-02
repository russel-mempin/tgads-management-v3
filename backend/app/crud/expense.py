from sqlmodel import Session, select
from app.models import Expense, ExpenseBase, AuditLog, Account, AccountTransaction
from app.enums import TransactionSource
from app.schemas.expense import ExpenseCreate
import uuid
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta


def get_all_expenses(db: Session, offset: int = 0, limit: int = 100) -> list[Expense]:
    return list(
        db.exec(
            select(Expense)
            .where(Expense.is_archived == False)
            .offset(offset)
            .limit(limit)
        ).all()
    )
    
def get_today_expenses(db: Session) -> list[Expense]:
    start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end = start + timedelta(days=1)

    return list(
        db.exec(
            select(Expense)
            .where(
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
            raise ValueError(f"Fund source not found in database")

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
        audit = AuditLog(action=f"Created expense", user_id=current_user_id)
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
        old_account = db.exec(select(Account).where(Account.id == expense.account_id)).first()
        if old_account:
            old_account.current_balance += expense.amount  # add back the old amount
            db.add(old_account)

            reversal = AccountTransaction(
                account_id=old_account.id,
                date=datetime.now(timezone.utc),
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
        new_account = db.exec(select(Account).where(Account.id == data.fund_source)).first()
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

        audit = AuditLog(action=f"Updated expense: {expense.description}", user_id=current_user_id)
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
        account = db.exec(select(Account).where(Account.id == expense.account_id)).first()
        if account:
            account.current_balance += expense.amount  # add back the amount
            db.add(account)

            reversal = AccountTransaction(
                account_id=account.id,
                date=datetime.now(timezone.utc),
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