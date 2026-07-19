import csv
import os
from sqlmodel import Session, select
from app.database import engine
from app.models import ExtraService
from app.utils.utils import to_float

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "extra_types.csv")

def seed_extra_services_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            existing = session.exec(
                select(ExtraService).where(
                    ExtraService.name == row["name"]
                )
            ).first()

            if existing:
                continue

            extra_type = ExtraService(
                name=row["name"],
                price=to_float(row["price"]),
            )

            session.add(extra_type)

        session.commit()