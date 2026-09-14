from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.enums import DatePeriod, TransactionSource
from app.models import AccountTransaction
from app.schemas.transaction import TransactionPublic
from app.utils.utils import get_date_range


def get_all_transactions(
    db: Session,
    period: DatePeriod = DatePeriod.ALL,
    source: TransactionSource | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[TransactionPublic]:

    statement = select(AccountTransaction).options(
        selectinload(AccountTransaction.account)
    )

    if period != DatePeriod.ALL:
        start, end = get_date_range(period)

        statement = statement.where(
            AccountTransaction.date >= start,
            AccountTransaction.date < end,
        )

    if source:
        statement = statement.where(
            AccountTransaction.source_type == source
        )

    statement = (
        statement
        .order_by(AccountTransaction.date.desc())
        .offset(offset)
        .limit(limit)
    )

    transactions = db.exec(statement).all()

    return [
        TransactionPublic.model_validate(transaction)
        for transaction in transactions
    ]