from datetime import date

from sqlalchemy import func
from sqlmodel import Session, select

from app.enums import JobStatus, TransactionSource
from app.models import (
    Account,
    AccountTransaction,
    Expense,
    JobItem,
    JobOrder,
    Payment,
    Service,
)
from app.schemas.dashboard import AccountData, OwnerDashboard, ServiceSales


def get_owner_dashboard_data(
    db: Session
) -> OwnerDashboard:
    today = date.today()
    month_start = today.replace(day=1)
    year_start = date(today.year, 1, 1)
    next_year = date(today.year + 1, 1, 1)

    # Account balances
    statement = (
        select(
            Account.name,
            (
                Account.beginning_balance
                + func.coalesce(func.sum(AccountTransaction.amount), 0)
            ).label("current_balance"),
        )
        .outerjoin(AccountTransaction, AccountTransaction.account_id == Account.id)
        .group_by(Account.id, Account.name, Account.beginning_balance)
    )
    balances = db.exec(statement).all()

    # Collections today
    collections_today = db.exec(
        select(func.coalesce(func.sum(AccountTransaction.amount), 0))
        .where(
            AccountTransaction.source_type.in_([
                TransactionSource.PAYMENT,
                TransactionSource.MISC_SALE,
            ]),
            func.date(AccountTransaction.date) == today,
        )
    ).one()

    # Collections this month
    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)
    collections_this_month = db.exec(
        select(func.coalesce(func.sum(AccountTransaction.amount), 0))
        .where(
            AccountTransaction.source_type.in_([
                TransactionSource.PAYMENT,
                TransactionSource.MISC_SALE,
            ]),
            AccountTransaction.date >= month_start,
            AccountTransaction.date < next_month,
        )
    ).one()

    # Outstanding receivables (TODO: Possibly wrong)
    outstanding_receivables = db.exec(
        select(
            func.coalesce(
                func.sum(JobItem.subtotal), 0
            ) - func.coalesce(
                func.sum(Payment.amount), 0
            )
        )
        .select_from(JobOrder)
        .outerjoin(JobItem, JobItem.job_order_id == JobOrder.id)
        .outerjoin(Payment, Payment.job_order_id == JobOrder.id)
        .where(JobOrder.voided_at.is_(None))
    ).one()

    # Expenses this month
    expenses_this_month = db.exec(
        select(func.coalesce(func.sum(Expense.amount), 0))
        .where(
            Expense.date >= month_start,
            Expense.date < next_month,
            Expense.is_archived == False,
        )
    ).one()

    # Sales per services
    sales_per_service = db.exec(
        select(
            Service.abbreviation.label("service_abbreviation"),
            func.coalesce(func.sum(JobItem.subtotal), 0).label("amount"),
        )
        .join(JobItem, JobItem.service_id == Service.id)
        .join(JobOrder, JobItem.job_order_id == JobOrder.id)
        .where(
            JobOrder.date_received >= year_start,
            JobOrder.date_received < next_year,
            JobOrder.voided_at.is_(None),
            JobItem.job_status != JobStatus.CANCELLED,
        )
        .group_by(Service.id, Service.name, Service.abbreviation)
        .order_by(func.sum(JobItem.subtotal).desc())
    ).all()

    # Count of overdue jobs
    jobs = db.exec(
        select(JobOrder)
        .where(JobOrder.voided_at.is_(None))
    ).all()
    overdue_jobs = sum(
        1 for job in jobs
        if any(
            item.due_date
            and item.due_date.date() < today
            and item.job_status not in {
                JobStatus.RELEASED,
                JobStatus.CANCELLED,
            }
            for item in job.job_items
        )
    )

    # Count of pending jobs
    pending_jobs = db.exec(
        select(func.count(JobOrder.id))
        .where(
            JobOrder.voided_at.is_(None),
            JobOrder.overall_job_status != JobStatus.RELEASED,
            JobOrder.overall_job_status != JobStatus.CANCELLED
        )
    ).one()

    return OwnerDashboard(
        accounts_balances=[
            AccountData(
                account_name=row.name,
                current_balance=row.current_balance,
            )
            for row in balances
        ],
        collections_today=collections_today,
        collections_this_month=collections_this_month,
        outstanding_receivables=outstanding_receivables,
        expenses_this_month=expenses_this_month,
        sales_per_service=[
            ServiceSales(
                service_abbreviation=row.service_abbreviation,
                amount=row.amount,
            )
            for row in sales_per_service
        ],
        overdue_jobs=overdue_jobs,
        pending_jobs=pending_jobs,
    )