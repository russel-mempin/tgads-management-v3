from sqlmodel import Session, select
from app.models import Expense


def get_all_expenses(
    db: Session, offset: int = 0, limit: int = 100
) -> list[Expense]:
    return list(db.exec(
        select(Expense)
        .where(Expense.is_archived == False)
        .offset(offset)
        .limit(limit)
    ).all())