import csv, os
from sqlmodel import Session
from app.database import engine
from app.models import ServiceType

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "service_types.csv")

def to_float(v: str) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0

def seed_service_types_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            service_type = ServiceType(
				name=row["name"],
				price=to_float(row["price"]),
				unit=row["unit"]
			)
            session.add(service_type)
        session.commit()