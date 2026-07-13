import os
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, select
from app.database import engine
from app.models import JobOrder, User
from app.seed_code.seed_users import seed_users_from_csv
from app.seed_code.seed_services import seed_services_data
from app.seed_code.seed_extra_services import seed_extra_services_from_csv
from app.seed_code.seed_payments import seed_payments_from_csv
from app.seed_code.seed_claiming_history import seed_claiming_history_from_csv
from app.seed_code.seed_job_orders import seed_complete_job_order_info
from app.seed_code.seed_expenses import seed_expenses_from_csv
from app.seed_code.seed_accounts import seed_accounts

BASE_DIR = os.path.dirname(__file__)
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH, override=True)
ENV = os.getenv("APP_ENV")

def seed_dev_data():
    if ENV == "test":
        # Always reseed for test
        SQLModel.metadata.drop_all(engine)
        print("Dropped all tables.")
        SQLModel.metadata.create_all(engine)
        print("Created all tables.")

        seed_users_from_csv()
        print("Seeded users.")
        seed_services_data()
        print("Seeded services.")
        seed_extra_services_from_csv()
        print("Seeded extra services.")
        seed_accounts()
        print("Seeded accounts.")
        seed_complete_job_order_info()
        print("Seeded job orders.")
        seed_payments_from_csv()
        print("Seeded payments.")
        # seed_claiming_history_from_csv()
        # print("Seeded claiming history.")
        # seed_expenses_from_csv()
        # print("Seeded expenses.")

    else:
        # Create tables if they don't exist
        SQLModel.metadata.create_all(engine)
        print("Created tables. (Development)")

        # Only seed if database is empty
        with Session(engine) as session:
            existing = session.exec(select(JobOrder)).first()
            if existing:
                print("Data already exists, skipping seed.")
                return

        print("No data found, seeding...")
        seed_users_from_csv()
        print("Seeded users.")
        seed_service_types_from_csv()
        print("Seeded service types.")
        seed_extra_types_from_csv()
        print("Seeded extra types.")
        seed_accounts()
        print("Seeded accounts.")
        seed_complete_job_order_info()
        print("Seeded job orders.")
        seed_payments_from_csv()
        print("Seeded payments.")
        seed_claiming_history_from_csv()
        print("Seeded claiming history.")
        seed_expenses_from_csv()
        print("Seeded expenses.")
        
def seed_prod_data():
    SQLModel.metadata.create_all(engine)
    print("Created tables. (Production)")
    with Session(engine) as session:
        existing = session.exec(select(User)).first()
        if existing:
            print("Production data already exists, skipping seed.")
            return
    
    SQLModel.metadata.create_all(engine)
    print("Created tables.")
    seed_users_from_csv()
    print("Seeded users.")
    seed_service_types_from_csv()
    print("Seeded service types.")
    seed_extra_types_from_csv()
    print("Seeded extra types.")
    seed_accounts()
    print("Seeded accounts.")