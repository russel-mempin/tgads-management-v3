from datetime import date
from decimal import Decimal

from sqlalchemy import case, func
from sqlmodel import Session, select

from app.enums import TransactionSource
from app.models import AccountTransaction
from app.schemas.performance import MonthlyPerformanceBase


def get_monthly_performance_list(
    db: Session,
    year: int
) -> list[MonthlyPerformanceBase]:

    collected = func.coalesce(
        func.sum(
            case(
                (
                    AccountTransaction.source_type.in_([
                        TransactionSource.PAYMENT,
                        TransactionSource.BANK_INTEREST,
                        TransactionSource.MISC_SALE,
                    ]),
                    AccountTransaction.amount,
                ),
                (
                    AccountTransaction.source_type == TransactionSource.REVERSAL,
                    case(
                        (AccountTransaction.amount < 0, AccountTransaction.amount),
                        else_=0,
                    ),
                ),
                else_=0,
            )
        ),
        0,
    )

    expenses = func.coalesce(
        func.sum(
            case(
                (
                    AccountTransaction.source_type.in_([
                        TransactionSource.EXPENSE,
                        TransactionSource.REFUND,
                    ]),
                    func.abs(AccountTransaction.amount),
                ),
                (
                    AccountTransaction.source_type == TransactionSource.REVERSAL,
                    case(
                        (AccountTransaction.amount > 0, -AccountTransaction.amount),
                        else_=0,
                    ),
                ),
                else_=0,
            )
        ),
        0,
    )

    statement = (
        select(
            func.extract(
                "month", AccountTransaction.date
            ).label("month"),
            collected.label("collected"),
            expenses.label("expenses"),
        )
        .where(
            AccountTransaction.date >= date(year, 1, 1),
            AccountTransaction.date < date(year + 1, 1, 1),
        )
        .group_by(
            func.extract("month", AccountTransaction.date)
        )
        .order_by(
            func.extract("month", AccountTransaction.date)
        )
    )

    results = db.exec(statement).all()

    monthly_data = {
        int(row.month): row
        for row in results
    }

    return [
        MonthlyPerformanceBase(
            month=date(year, month, 1).strftime("%B"),
            collected=monthly_data[month].collected if month in monthly_data else Decimal("0.00"),
            expenses=monthly_data[month].expenses if month in monthly_data else Decimal("0.00"),
            net=(
                monthly_data[month].collected - monthly_data[month].expenses
            ) if month in monthly_data else Decimal("0.00"),
            sales=0,
            receivables=0
        )
        for month in range(1, 13)
    ]