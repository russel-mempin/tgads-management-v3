import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import JobOrder, JobItem, ServiceType, ExtraType, SizeUnit, JobStatus, PaymentStatus, PaperSize
from app.utils.utils import to_float, to_int
from datetime import datetime

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
                job_order_id=jo_number.id,
                service_type_id=service_type.id,
                extra_type_id=extra_type.id,
                description=row["description"],
                height=to_float(row["height"]),
                width=to_float(row["width"]),
                size_unit=SizeUnit(row["size_unit"]),
                paper_size=PaperSize(row["paper_size"]),
                unit_price=to_float(row["unit_price"]),
                quantity=to_int(row["quantity"]),
                subtotal=to_float(row["unit_price"]) * to_int(row["quantity"]) + to_float(row["extra_type_price"]) - to_float(row["discount"]),
                job_status=JobStatus(row["job_status"]),
                payment_status=PaymentStatus(row["payment_status"]),
                due_date=datetime.fromisoformat(row["due_date"]),
                extra_type_price=to_float(row["extra_type_price"]),
                discount=to_float(row["discount"])
            )
            session.add(job_item)
        session.commit()
