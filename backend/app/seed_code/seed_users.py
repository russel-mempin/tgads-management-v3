import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import User, UserRoles
from app.services.auth import get_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "users.csv")

def seed_users_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            existing_user = session.exec(
                select(User).where(User.email == row["email"])
            ).first()

            if existing_user:
                continue

            user = User(
                first_name=row["first_name"],
                last_name=row["last_name"],
                username=row["username"],
                email=row["email"],
                role=UserRoles(row["role"]),
                is_active=row["is_active"].lower() == "true",
                is_superAdmin=row["is_super"].lower() == "true",
                hashed_password=get_password_hash(row["password"]),
            )

            session.add(user)
            print(f"Added user named {user.first_name} {user.last_name}.")

        session.commit()