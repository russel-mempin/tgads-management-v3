import csv, os
from sqlmodel import Session
from app.database import engine
from app.models import ExtraType
from app.utils.utils import to_float

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "extra_types.csv")

def seed_extra_types_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            extra_type = ExtraType(
				name=row["name"],
				price=to_float(row["price"]),
			)
            session.add(extra_type)
        session.commit()