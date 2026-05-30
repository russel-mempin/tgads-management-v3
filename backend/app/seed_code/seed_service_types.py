import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import ServiceType, SizeUnit
from app.utils.utils import to_float

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "service_types.csv")

def seed_service_types_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            existing = session.exec(
                select(ServiceType).where(
                    ServiceType.name == row["name"]
                )
            ).first()

            if existing:
                continue

            service_type = ServiceType(
                name=row["name"],
                abbreviation=row["abbreviation"],
                price=to_float(row["price"]),
                unit=row["unit"],
                required_measurement_unit=SizeUnit(
                    row["required_measurement_unit"]
                ),
            )

            session.add(service_type)

        session.commit()