import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import Customer, JobOrder, User
from datetime import datetime
from app.utils.utils import to_int

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_orders.csv")


def seed_job_orders_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customer = session.exec(
                select(Customer).where(Customer.name == row["customer_name"])
            ).first()
            user = session.exec(
                select(User).where(User.first_name == "Russel")
            ).first()
            print(f"Found user: {user}")
            if not user:
                print("User not found.")
                return
            if not customer:
                print(f"Customer not found: {row['customer_name']}")
                continue
            user_id = user.id
            job_order = JobOrder(
                jo_number=to_int(row["jo_number"]),
                date_received=datetime.fromisoformat(row["date_received"]),
                customer_id=customer.id,
                is_active=row["is_active"].strip().lower() == "true",
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            session.add(job_order)
        session.commit()
