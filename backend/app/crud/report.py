from sqlmodel import Session, select, col
from sqlalchemy import func
from datetime import datetime, timezone
from app.models import Payment, Expense, JobOrder
from app.enums import PaymentMethod


def get_daily_report(db: Session, date: datetime) -> dict:
    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

    payments = db.exec(
        select(Payment).where(
            Payment.date_received >= day_start,
            Payment.date_received <= day_end,
        )
    ).all()

    expenses = db.exec(
        select(Expense).where(
            Expense.date >= day_start,
            Expense.date <= day_end,
            Expense.is_archived == False,
        )
    ).all()

    cash_payments = [p for p in payments if p.method == PaymentMethod.CASH]
    cheque_payments = [p for p in payments if p.method == PaymentMethod.CHEQUE]
    gcash_payments = [p for p in payments if p.method == PaymentMethod.GCASH]

    total_cash = sum(p.amount for p in cash_payments)
    total_cheque = sum(p.amount for p in cheque_payments)
    total_gcash = sum(p.amount for p in gcash_payments)
    total_expenses = sum(e.amount for e in expenses)

    total_sales = total_cash + total_cheque + total_gcash
    ending_balance = total_cash - total_expenses  # adjust based on what "ending balance" means to you

    return {
        "date": day_start,
        "cash_payments": cash_payments,
        "cheque_payments": cheque_payments,
        "gcash_payments": gcash_payments,
        "expenses": expenses,
        "total_cash": total_cash,
        "total_cheque": total_cheque,
        "total_gcash": total_gcash,
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "ending_balance": ending_balance,
    }