import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import JobOrder, Payment, PaymentMethod
from app.utils.utils import to_float
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "payments.csv")

def seed_payments_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            job_order = session.exec(
                select(JobOrder).where(JobOrder.jo_number == row["jo_number"])
            ).first()
            if not job_order:
                print(f"Job order not found: {row['jo_number']}")
                continue
            payment = Payment(
                date_received=datetime.fromisoformat(row["date_received"]),
                method=PaymentMethod(row["method"]),
                amount=to_float(row["amount"]),
                job_order_id=job_order.id
            )
            session.add(payment)
        session.commit()
