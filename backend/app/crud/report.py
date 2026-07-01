from sqlmodel import Session, select
from datetime import datetime
from app.models import Payment, Expense
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

    def enrich_payment(p: Payment) -> dict:
        return {
            "id": p.id,
            "date_received": p.date_received,
            "reference_number": p.reference_number,
            "method": p.method,
            "amount": p.amount,
            "customer_name": p.job_order.customer_name,
            "jo_number": p.job_order.jo_number,
        }

    cash_payments = [enrich_payment(p) for p in payments if p.method == PaymentMethod.CASH]
    cheque_payments = [enrich_payment(p) for p in payments if p.method == PaymentMethod.CHEQUE]
    gcash_payments = [enrich_payment(p) for p in payments if p.method == PaymentMethod.GCASH]

    total_cash = sum(p.amount for p in payments if p.method == PaymentMethod.CASH)
    total_cheque = sum(p.amount for p in payments if p.method == PaymentMethod.CHEQUE)
    total_gcash = sum(p.amount for p in payments if p.method == PaymentMethod.GCASH)
    total_expenses = sum(e.amount for e in expenses)

    total_sales = total_cash + total_cheque + total_gcash
    ending_balance = total_cash - total_expenses

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