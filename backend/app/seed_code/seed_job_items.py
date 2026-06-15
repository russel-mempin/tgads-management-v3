import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import JobOrder, JobItem, ServiceType, ExtraType
from app.utils.utils import to_float, to_int
from datetime import datetime
from app.enums import SizeUnit, JobStatus

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_items.csv")

def seed_job_items_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jo_number = session.exec(
                select(JobOrder).where(JobOrder.jo_number == row["jo_number"])
            ).first()
            service_type = session.exec(
                select(ServiceType).where(ServiceType.name == row["service_type"])
            ).first()
            extra_type = session.exec(
                select(ExtraType).where(ExtraType.name == row["extra_type"])
            ).first()
            if not jo_number:
                print(f"JO Number not found: {row['jo_number']}")
                continue
            if not service_type:
                print(f"Service type not found: {row['service_type']}")
                continue
            if not extra_type:
                print(f"Extra type not found: {row['extra_type']}")
                continue
            job_item = JobItem(
                jo_number=row["jo_number"],
                item_id=row["item_id"],
                job_order_id=jo_number.id,
                service_type_id=service_type.id,
                extra_type_id=extra_type.id,
                description=row["description"],
                height=to_float(row["height"]),
                width=to_float(row["width"]),
                size_unit=SizeUnit(row["size_unit"]),
                quantity=to_int(row["quantity"]),
                job_status=JobStatus(row["job_status"]),
                due_date=datetime.fromisoformat(row["due_date"]),
                discount=to_float(row["discount"]),
                notes=row["notes"]
            )
            session.add(job_item)
        session.commit()
