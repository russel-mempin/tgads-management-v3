import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import Customer, JobOrder
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_orders.csv")

def seed_job_orders_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customer = session.exec(
				select(Customer).where(Customer.name == row ["customer_name"])
			).first()
            if not customer:
                print(f"Customer not found: {row['customer_name']}")
                continue
            job_order = JobOrder(
                jo_number=row["jo_number"],
                date_received=datetime.fromisoformat(row["date_received"]),
                customer_id=customer.id,
            )
            session.add(job_order)
        session.commit()
