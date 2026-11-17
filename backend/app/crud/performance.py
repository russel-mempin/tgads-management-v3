from datetime import date
from decimal import Decimal

from sqlalchemy import case, func
from sqlmodel import Session, select

from app.enums import TransactionSource
from app.models import AccountTransaction, JobItem, JobOrder, Payment
from app.schemas.performance import MonthlyPerformance, MonthlyPerformanceBase


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
            func.extract("month", AccountTransaction.date).label("month"),
            collected.label("collected"),
            expenses.label("expenses"),
        )
        .where(
            AccountTransaction.date >= date(year, 1, 1),
            AccountTransaction.date < date(year + 1, 1, 1),
        )
        .group_by(func.extract("month", AccountTransaction.date))
        .order_by(func.extract("month", AccountTransaction.date))
    )

    results = db.exec(statement).all()

    monthly_data = {int(row.month): row for row in results}

    performance = []

    for month in range(1, 13):
        month_start = date(year, month, 1)

        next_month = (
            date(year + 1, 1, 1)
            if month == 12
            else date(year, month + 1, 1)
        )

        # Total value of job orders received this month
        job_totals = (
            select(
                JobItem.job_order_id,
                func.sum(JobItem.subtotal).label("total_due"),
            )
            .group_by(JobItem.job_order_id)
            .subquery()
        )

        # Payments received up to the end of this month
        payment_totals = (
            select(
                Payment.job_order_id,
                func.sum(Payment.amount).label("total_paid"),
            )
            .where(Payment.date_received < next_month)
            .group_by(Payment.job_order_id)
            .subquery()
        )

        job_performance = (
            select(
                func.coalesce(
                    func.sum(job_totals.c.total_due), 0
                ).label("sales"),
                func.coalesce(
                    func.sum(
                        job_totals.c.total_due
                        - func.coalesce(payment_totals.c.total_paid, 0)
                    ),
                    0,
                ).label("receivables"),
            )
            .select_from(JobOrder)
            .outerjoin(
                job_totals,
                job_totals.c.job_order_id == JobOrder.id,
            )
            .outerjoin(
                payment_totals,
                payment_totals.c.job_order_id == JobOrder.id,
            )
            .where(
                JobOrder.date_received >= month_start,
                JobOrder.date_received < next_month,
            )
        )

        job_result = db.exec(job_performance).one()

        transaction = monthly_data.get(month)

        collected_amount = (
            transaction.collected if transaction else Decimal("0.00")
        )
        expenses_amount = (
            transaction.expenses if transaction else Decimal("0.00")
        )

        performance.append(
            MonthlyPerformanceBase(
                month=month_start.strftime("%B"),
                collected=collected_amount,
                expenses=expenses_amount,
                net=collected_amount - expenses_amount,
                sales=job_result.sales,
                receivables=job_result.receivables,
            )
        )

    return performance


def get_months_performance(db: Session, year: int, month: int) -> MonthlyPerformance:
    pass