import csv
import os
from sqlmodel import Session, select
from app.database import engine
from datetime import datetime, timezone
from app.models import (
    Customer,
    VoidJobOrder,
    JobOrder,
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JOB_ORDERS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_orders.csv")
JOB_ITEMS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_items.csv")

VOID_REASONS = {
    "1": "No physical paper on Job pile",
    "2": "Listed as cancelled",
    "3": "Duplicate",
    "4": "Conflicting info on job summary excel and physical paper",
    "5": "Other"
}

# Helper functions
def parse_date(value: str) -> datetime:
    dt = datetime.strptime(value.strip(), "%m/%d/%y")
    return dt.replace(tzinfo=timezone.utc)

def get_or_create_customer(session: Session, customer_name: str) -> Customer:
    customer_name = customer_name.strip()
    existing = session.exec(select(Customer).where(Customer.name == customer_name)).first()
    if existing:
        return existing
    customer = Customer(name=customer_name)
    session.add(customer)
    session.flush()
    return customer
    

def seed_job_orders(file_path: str = JOB_ORDERS_CSV_PATH) -> dict[str, int]:
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_received = parse_date(row["date"])
            jo_number = int(row["jo_number"].strip())
            customer_name = (row["customer_name"] or "").strip()
            void_choice = row["void_choice"].strip()
            
            # If no customer, inserts job data to void table and determines void reason.
            if not customer_name:
                existing_in_void = session.exec(
                    select(VoidJobOrder).where(VoidJobOrder.jo_number == jo_number)
                ).first()
                if not existing_in_void:
                    # If and elif block could be deleted for automation
                    if void_choice:
                        # Determine reason here
                        reason = VOID_REASONS[void_choice]
                        print(f"JO {jo_number} has been inserted to void job orders table.")
                    else:
                        while True:
                            print(f"\n JO #{jo_number} has no customer name. This would be inserted in the Void Job Orders table.")
                            print("\n Select a reason:")
                            
                            for key, value in VOID_REASONS.items():
                                print(f"[{key}] {value}")
                                
                            choice = input("> ").strip()
                            
                            if choice in VOID_REASONS:
                                if choice == "5":
                                    reason = input("Enter custom reason: ").strip()
                                else:
                                    reason = VOID_REASONS[choice]
                                break
                            print("Invalid choice. Try again.")
                    session.add(VoidJobOrder(
                        jo_number=jo_number,
                        job_date=date_received,
                        reason=reason
                    ))
                    session.commit()
                    continue
                
            # If negative JO number, mark as unlogged 
                
            # Else, insert data normally
            customer = get_or_create_customer(session, customer_name)
            session.add(JobOrder(
                date_received=date_received,
                jo_number=jo_number,
                customer=customer,
            ))
            