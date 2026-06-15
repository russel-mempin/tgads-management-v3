import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import Customer, JobOrder, JobItem, ServiceType, ExtraType
from datetime import datetime
from app.enums import SizeUnit, JobStatus
from app.utils.utils import to_float, to_int


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CSV_FILES = [
	os.path.join(BASE_DIR, "seed_data", "january2026.csv"),
	os.path.join(BASE_DIR, "seed_data", "february2026.csv"),
	os.path.join(BASE_DIR, "seed_data", "march2026.csv"),
	os.path.join(BASE_DIR, "seed_data", "june2026.csv"),
]

UNIT_MAP = {
	"in": SizeUnit.INCHES,
	"in.": SizeUnit.INCHES,
	"ft": SizeUnit.FEET,
	"ft.": SizeUnit.FEET,
	"cm": SizeUnit.CENTIMETER,
	"cm.": SizeUnit.CENTIMETER,
	"mm": SizeUnit.MILLIMETER,
	"mm.": SizeUnit.MILLIMETER,
	"n/a": SizeUnit.NA,
}

def seed_job_orders_from_converted_excel():
    service_instance_counter = {}    
    for file_path in CSV_FILES:
        print(f"Seeding {file_path}...")
        _seed_file(file_path, service_instance_counter)

def _seed_file(file_path: str, service_instance_counter: dict):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        last_date = datetime.now()  # fallback if first row is empty

        for row in reader:
            if row["Date"].strip():
                last_date = datetime.strptime(row["Date"], "%m/%d/%y")
            customer = session.exec(
                select(Customer).where(Customer.name == row["Customer"])
            ).first()
            if not customer:
                customer = Customer(name=row["Customer"])
                session.add(customer)
                session.commit()
                session.flush()

            joborder = session.exec(
                select(JobOrder).where(JobOrder.jo_number == row["JO No."])
            ).first()
            if not joborder:
                joborder = JobOrder(
                    jo_number=row["JO No."],
                    customer_id=customer.id,
                    date_received=datetime.strptime(row["Date"], "%m/%d/%y") if row["Date"].strip() else last_date,
                )
                session.add(joborder)
                session.commit()
                session.flush()

            service_type = session.exec(
                select(ServiceType).where(ServiceType.name == row["Service"])
            ).first()

            if not service_type:
                print(f"ServiceType not found: {row['Service']}. Skipping row.")
                continue

            extra_type = session.exec(
                select(ExtraType).where(ExtraType.name == row["Extra Service"])
            ).first()

            counter_key = (joborder.jo_number, service_type.abbreviation)
            service_instance_counter[counter_key] = (
                service_instance_counter.get(counter_key, 0) + 1
            )
            instance_num = service_instance_counter[counter_key]

            assembled_item_id = (
                f"{joborder.jo_number}-{service_type.abbreviation}-{instance_num}"
            )
            
            size_unit = UNIT_MAP.get(row["Unit"].strip().lower(), SizeUnit.NA)  # default to NA if empty

            if size_unit is None:
                print(f"Unknown unit: {row['Unit']}. Skipping row.")
                continue

            jobitem = JobItem(
                jo_number=joborder.jo_number,
                item_id=assembled_item_id,
                job_order_id=joborder.id,
                service_type_id=service_type.id,
                extra_type_id=extra_type.id if extra_type else None,
                description=row["Description"],
                size_unit=size_unit,
                job_status=JobStatus.CANCELLED if service_type.name == "Cancelled" else JobStatus.RELEASED,
                height=to_float(row["Height"]),
                width=to_float(row["Width"]),
                quantity=to_int(row["Qty"]),
                discount=to_float(row["Discount"]),
                extra_charge=to_float(row["Extra Charge"])
            )
            session.add(jobitem)

        session.commit()