from typing import cast

from sqlalchemy.orm import InstrumentedAttribute, selectinload
from sqlmodel import Session, func, select

from app.enums import DatePeriod, TransactionSource
from app.models import AccountTransaction
from app.schemas.transaction import TransactionList, TransactionPublic
from app.utils.utils import get_date_range


def get_all_transactions(
    db: Session,
    period: DatePeriod = DatePeriod.ALL,
    category: TransactionSource | None = None,
    offset: int = 0,
    limit: int = 100,
) -> TransactionList:
    statement = select(AccountTransaction).options(
        selectinload(
            cast(InstrumentedAttribute, AccountTransaction.account)
        )
    )

    if period != DatePeriod.ALL:
        date_range = get_date_range(period)

        if date_range:
            start, end = date_range
            statement = statement.where(
                AccountTransaction.date >= start,
                AccountTransaction.date < end,
            )

    if category:
        statement = statement.where(
            AccountTransaction.source_type == category
        )

    # Count all matching records before pagination
    total = db.exec(
        select(func.count()).select_from(statement.subquery())
    ).one()

    # Fetch the current page
    transactions = db.exec(
        statement
        .order_by(AccountTransaction.date.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return TransactionList(
        items=[
            TransactionPublic.model_validate(transaction)
            for transaction in transactions
        ],
        total=total,
    )