import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import JobOrder, Payment, Account
from app.utils.utils import to_float
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "june2026payments.csv")

def seed_payments_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        touched_job_orders = set()
        
        METHOD_TO_ACCOUNT = {
            "Cash": "Cash",
            "GCash": "GCash",
            "Cheque": "RCBC",
        }
        for row in reader:
            if not row["JO Number"]:
                print(f"No JO number for payment of {row['Customer Name']} amounting to {row['Amount']}. Skipped.")
                continue
            ref = row.get("Reference Number") or ""
            if not ref.strip():
                print(f"No reference number for payment of {row['Customer Name']} amounting to {row['Amount']}. Skipped.")
                continue
            job_order = session.exec(
                select(JobOrder).where(JobOrder.jo_number == row["JO Number"])
            ).first()
            if not job_order:
                print(f"Job order not found: {row['JO Number']}")
                continue
            
            account_name = METHOD_TO_ACCOUNT.get(row["Method"])
            if not account_name:
                raise ValueError(f"No account mapped for method: {row['Method']}")
            account = session.exec(
                select(Account).where(Account.name == account_name)
            ).first()
            if not account:
                raise ValueError(f"Account '{account_name}' not found in database")
            payment = Payment(
                date_received=datetime.strptime(row["Date"], "%m/%d/%y"),
                amount=to_float(row["Amount"]),
                reference_number=row["Reference Number"],
                job_order_id=job_order.id,
                account_id=account.id
            )
            print(f"Added payment from: {row['Customer Name']} amounting to: {row['Amount']}")
            session.add(payment)
            touched_job_orders.add(job_order.id)

        session.commit()

        for jo_id in touched_job_orders:
            job_order = session.get(JobOrder, jo_id)
            if job_order:
                job_order.sync_computed_fields()
                session.add(job_order)

        session.commit()