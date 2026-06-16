import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import JobOrder, Payment, PaymentMethod
from app.utils.utils import to_float
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "june2026payments.csv")

def seed_payments_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        touched_job_orders = set()

        for row in reader:
            if not row["JO Number"]:
                print(f"No JO number for payment of {row['Customer Name']} amounting to {row['Amount']}. Skipped.")
                continue
            job_order = session.exec(
                select(JobOrder).where(JobOrder.jo_number == row["JO Number"])
            ).first()
            if not job_order:
                print(f"Job order not found: {row['JO Number']}")
                continue
            payment = Payment(
                date_received=datetime.strptime(row["Date"], "%m/%d/%y"),
                method=PaymentMethod(row["Method"]),
                amount=to_float(row["Amount"]),
                job_order_id=job_order.id
            )
            print(f"Added payment from: {row['Customer Name']} amounting to: {row['Amount']}")
            session.add(payment)
            touched_job_orders.add(job_order.id)

        session.commit()

        # Sync computed fields for every job order that got a payment
        for jo_id in touched_job_orders:
            job_order = session.get(JobOrder, jo_id)
            if job_order:
                job_order.sync_computed_fields()
                session.add(job_order)

        session.commit()