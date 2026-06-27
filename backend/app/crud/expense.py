from sqlmodel import Session, select
from app.models import Expense, ExpenseBase, AuditLog
import uuid
from fastapi import HTTPException


def get_all_expenses(
    db: Session, offset: int = 0, limit: int = 100
) -> list[Expense]:
    return list(db.exec(
        select(Expense)
        .where(Expense.is_archived == False)
        .offset(offset)
        .limit(limit)
    ).all())
    
    
def create_expense(db: Session, data: ExpenseBase, current_user_id: uuid.UUID):
    try:
        expense = Expense(
            date=data.date,
            category=data.category,
            amount=data.amount,
            description=data.description
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        
        audit = AuditLog(
            action=f"Created expense", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        
        return expense
    except Exception:
        db.rollback()
        raise
    
    
def update_expense(db: Session, expense_id: uuid.UUID, data: ExpenseBase, current_user_id: uuid.UUID):
    try:
        expense = db.exec(
            select(Expense).where(Expense.id == expense_id)
        ).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Misc sale not found.")
        
        expense.date = data.date
        expense.category = data.category
        expense.amount = data.amount
        expense.description = data.description
        
        db.add(expense)
        db.commit()
        db.refresh(expense)
        
        audit = AuditLog(
            action=f"Updated expense", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        
        return expense
    except Exception:
        db.rollback()
        raise


def archive_expense(db: Session, expense_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        expense = db.exec(
            select(Expense).where(Expense.id == expense_id)
        ).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Misc sale not found")

        expense.is_archived = True
        db.add(expense)

        audit = AuditLog(
            action=f"Deleted misc_sale {expense.description}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        db.refresh(expense)
        return "Expense deleted."
    except HTTPException:
        raise  # don't rollback for 404s, nothing was changed
    except Exception:
        db.rollback()
        raise