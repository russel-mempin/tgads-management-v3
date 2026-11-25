import csv
import os
from decimal import Decimal

from sqlmodel import Session, select

from app.database import engine
from app.enums import ReasonCategory, ReviewEntityType, TransactionSource
from app.models import (
    Account,
    AccountTransaction,
    ForReview,
    JobOrder,
    MiscSale,
    Payment,
    Receipts,
    UnlinkedPayment,
    User,
)
from app.utils.utils import get_system_admin, parse_currency, parse_date

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PAYMENTS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "billingandinvoice.csv")


def get_account(session: Session, method: str) -> Account | None:
    return session.exec(
        select(Account).where(Account.name == method.strip())
    ).first()


def get_user_from_signatory(session: Session, full_name: str) -> User | None:
    parts = full_name.strip().split(maxsplit=1)

    if len(parts) != 2:
        return None

    first_name, last_name = parts

    return session.exec(
        select(User).where(
            User.first_name == first_name,
            User.last_name == last_name,
        )
    ).first()


def seed_payments_from_csv(file_path: str = PAYMENTS_CSV_PATH):
    with Session(engine) as session:
        sysadmin = get_system_admin(session)
        with open(file_path, newline="") as f:
            for row in csv.DictReader(f):
                method = (row.get("method") or "").strip() or "Cash"
                account = get_account(session, method)

                if account is None:
                    print(f"Account not found: {method}")
                    continue

                signatory_name = (row.get("signatory") or "").strip()
                signatory = get_user_from_signatory(session, signatory_name) if signatory_name else None

                date_received = parse_date(row["date_issued"])
                reference_number = row.get("reference_number", "").strip()
                description = row.get("description", "").strip()
                amount = parse_currency(row.get("total_amount", ""))
                jo_number_raw = row.get("jo_number", "").strip()
                is_misc_sale = (row.get("is_misc_sale") or "").strip().upper() == "TRUE"
                receipt_issued = Receipts(row["receipt_issued"])

                job_order = None
                if is_misc_sale:
                    misc_sale = MiscSale(
                        date=date_received,
                        description=description,
                        reference_number=reference_number,
                        amount=amount,
                        receipt_issued=Receipts(row["receipt_issued"]) if receipt_issued else None,
                        account_id=account.id,
                        account_name_snapshot=account.name,
                        signatory_id=signatory.id if signatory else None,
                        created_by_id=sysadmin.id
                    )
                    session.add(misc_sale)
                    session.flush()

                    session.add(
                        AccountTransaction(
                            account_id=account.id,
                            amount=Decimal(amount),
                            source_type=TransactionSource.MISC_SALE,
                            source_id=misc_sale.id,
                            date=date_received,
                            description=f"{row["name"]}: {description}",
                        )
                    )
                    continue

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
                        receipt_issued = Receipts(row["receipt_issued"]),
                        signatory_id=signatory.id if signatory else None,
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
                            date=date_received,
                            description=f"Payment for Job Order {job_order.jo_number}. Remaining balance: {job_order.balance}"
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
                        signatory_id=signatory.id if signatory else None,
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
