import csv
import os
from datetime import UTC, datetime
from decimal import Decimal

from sqlmodel import Session, select

from app.database import engine
from app.enums import ReasonCategory, ReviewEntityType, TransactionSource
from app.models import (
    Account,
    AccountTransaction,
    ForReview,
    JobOrder,
    Payment,
    UnlinkedPayment,
)
from app.utils.utils import get_system_admin, to_float

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PAYMENTS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "payments.csv")

ACCOUNT_NAME_BY_METHOD: dict[str, str] = {
    "Cash": "Cash",
    "GCash": "GCash",
    "Bank": "RCBC",
}


def parse_currency(value: str) -> float:
    cleaned = (value or "").replace("₱", "").replace(",", "").strip()
    return to_float(cleaned) if cleaned else 0.0


def parse_date(value: str) -> datetime:
    value = value.strip()

    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=UTC)
        except ValueError:
            pass

    raise ValueError(f"Unsupported date format: {value}")


def get_account(session: Session, method: str) -> Account | None:
    account_name = ACCOUNT_NAME_BY_METHOD.get(method.strip())
    if account_name is None:
        return None
    return session.exec(select(Account).where(Account.name == account_name)).first()


def seed_payments_from_csv(file_path: str = PAYMENTS_CSV_PATH):
    with Session(engine) as session:
        sysadmin = get_system_admin(session)
        with open(file_path, newline="") as f:
            for row in csv.DictReader(f):
                account = get_account(session, row.get("method", ""))
                if account is None:
                    print("Account not found.")
                    continue

                date_received = parse_date(row["date_received"])
                reference_number = row.get("reference_number", "").strip()
                amount = parse_currency(row.get("amount", ""))
                jo_number_raw = row.get("jo_number", "").strip()

                job_order = None
                if jo_number_raw:
                    job_order = session.exec(
                        select(JobOrder).where(JobOrder.jo_number == int(jo_number_raw))
                    ).first()

                if job_order:
                    existing = session.exec(
                        select(Payment).where(
                            Payment.job_order_id == job_order.id,
                            Payment.reference_number == reference_number,
                        )
                    ).first()
                    if existing:
                        continue

                    payment = Payment(
                        date_received=date_received,
                        reference_number=reference_number,
                        amount=Decimal(amount),
                        account_id=account.id,
                        job_order_id=job_order.id,
                        job_order=job_order,
                        account_name_snapshot=account.name,
                    )
                    session.add(payment)
                    session.flush()
                    job_order.sync_computed_fields()
                    session.add(
                        AccountTransaction(
                            account_id=account.id,
                            amount=Decimal(amount),
                            source_type=TransactionSource.PAYMENT,
                            source_id=payment.id,
                        )
                    )
                else:
                    description = row.get("description", "").strip() or None
                    if jo_number_raw:
                        note = f"[JO {jo_number_raw} referenced but not found] "
                        description = note + (description or "")
                    unlinked_payment = UnlinkedPayment(
                        date_received=date_received,
                        reference_number=reference_number,
                        amount=Decimal(amount),
                        customer_name=row.get("name", "").strip() or None,
                        description=description,
                        account_id=account.id,
                    )
                    session.add(unlinked_payment)

                    session.add(
                        ForReview(
                            entity_type=ReviewEntityType.PAYMENT,
                            entity_id=unlinked_payment.id,
                            created_by_id=sysadmin.id,
                            entity_reference=reference_number,
                            reason="No links to any job.",
                            reason_category=ReasonCategory.MISSING_DATA,
                        )
                    )
                    print(f"Unlinked Payment {reference_number} marked for review.")
        session.commit()
