import csv, os
from sqlmodel import Session
from app.database import engine
from app.models import User, UserRoles
from app.services.auth import get_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "users.csv")

def seed_users_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = User(
                first_name=row["first_name"],
                last_name=row["last_name"],
                username=row["username"],
                email=row["email"],
                role=UserRoles(row["role"]),
                is_active=row["is_active"].lower() == "true",
                hashed_password=get_password_hash(row["password"]),
            )
            session.add(user)
        session.commit()
