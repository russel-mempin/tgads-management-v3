import csv, os
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.database import engine
from app.models import Account, JobOrder, Payment, UnlinkedPayment
from app.utils.utils import to_float

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PAYMENTS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "payments.csv")

ACCOUNT_NAME_BY_METHOD: dict[str, str] = {
    "Cash": "Cash",
    "GCash": "GCash",
    "Bank": "BPI Savings",
}


def parse_currency(value: str) -> float:
    cleaned = (value or "").replace("₱", "").replace(",", "").strip()
    return to_float(cleaned) if cleaned else 0.0


def parse_date(value: str) -> datetime:
    dt = datetime.strptime(value.strip(), "%m/%d/%Y")
    return dt.replace(tzinfo=timezone.utc)


def get_account(session: Session, method: str) -> Account | None:
    account_name = ACCOUNT_NAME_BY_METHOD.get(method.strip())
    if account_name is None:
        return None
    return session.exec(select(Account).where(Account.name == account_name)).first()


def seed_payments_from_csv(file_path: str = PAYMENTS_CSV_PATH):
    skipped: list[str] = []
    linked_count = 0
    unlinked_count = 0

    with Session(engine) as session:
        with open(file_path, newline="") as f:
            for row in csv.DictReader(f):
                account = get_account(session, row.get("method", ""))
                if account is None:
                    skipped.append(f"Ref {row.get('reference_number', '?')}: "
                                    f"no account for method '{row.get('method', '')}'")
                    continue

                date_received = parse_date(row["date_received"])
                reference_number = row.get("reference_number", "").strip() or None
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

                    session.add(Payment(
                        date_received=date_received,
                        reference_number=reference_number,
                        amount=amount,
                        account_id=account.id,
                        job_order_id=job_order.id,
                    ))
                    linked_count += 1
                else:
                    description = row.get("description", "").strip() or None
                    if jo_number_raw:
                        note = f"[JO {jo_number_raw} referenced but not found] "
                        description = note + (description or "")

                    session.add(UnlinkedPayment(
                        date_received=date_received,
                        reference_number=reference_number,
                        amount=amount,
                        customer_name=row.get("name", "").strip() or None,
                        description=description,
                        account_id=account.id,
                    ))
                    unlinked_count += 1

        session.commit()

    print(f"Payments: {linked_count} linked to job orders, {unlinked_count} unlinked")
    if skipped:
        print(f"\n[WARN] {len(skipped)} rows skipped:")
        for s in skipped:
            print(f"  - {s}")