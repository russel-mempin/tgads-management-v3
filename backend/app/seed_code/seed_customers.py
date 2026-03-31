import csv, os
from sqlmodel import Session
from app.database import engine
from app.models import Customer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "customers.csv")

def seed_customers_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customer = Customer(
                name=row["name"],
                address=row["address"],
                contact_no=row["contact_no"],
                email=row["email"],
            )
            session.add(customer)
        session.commit()
