import os
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, select
from app.database import engine
from app.models import JobOrder
from app.seed_code.seed_users import seed_users_from_csv
from app.seed_code.seed_service_types import seed_service_types_from_csv
from app.seed_code.seed_extra_types import seed_extra_types_from_csv
from app.seed_code.seed_customers import seed_customers_from_csv
from app.seed_code.seed_payments import seed_payments_from_csv
from app.seed_code.seed_claiming_history import seed_claiming_history_from_csv
from app.seed_code.seed_from_converted import seed_job_orders_from_converted_excel

BASE_DIR = os.path.dirname(__file__)
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH, override=True)
ENV = os.getenv("APP_ENV")

def seed_dev_data():

    """
    1. users
    2. service_types
    3. extra_types
    4. customers
    5. job_orders
    6. job_items
    7. payments
    8. claiming_history
    """
    if ENV != "test":
        print("Entered dev environment.")
        SQLModel.metadata.drop_all(engine)
        print("Dropped all tables.")
        SQLModel.metadata.create_all(engine)
        print("Created all tables")

        seed_users_from_csv()
        print("Seeded users.")
        seed_service_types_from_csv()
        print("Seeded service types.")
        seed_extra_types_from_csv()
        print("Seeded extra types.")
        seed_customers_from_csv()
        print("Seeded customers.")
        seed_job_orders_from_converted_excel()
        print("Seeded job orders.")
        seed_payments_from_csv()
        print("Seeded payments.")
        seed_claiming_history_from_csv()
        print("Seeded claiming history.")

    with Session(engine) as session:
        existing = session.exec(select(JobOrder)).first()
        if existing:
            print("Data already exists, skipping initial seed.")
            return
        print("Entered dev environment.")
        SQLModel.metadata.drop_all(engine)
        print("Dropped all tables.")
        SQLModel.metadata.create_all(engine)
        print("Created all tables")

        seed_users_from_csv()
        print("Seeded users.")
        seed_service_types_from_csv()
        print("Seeded service types.")
        seed_extra_types_from_csv()
        print("Seeded extra types.")
        seed_customers_from_csv()
        print("Seeded customers.")
        seed_job_orders_from_converted_excel()
        print("Seeded job orders.")
        seed_payments_from_csv()
        print("Seeded payments.")
        seed_claiming_history_from_csv()
        print("Seeded claiming history.")
        
def seed_prod_data():
    with Session(engine) as session:
        existing = session.exec(select(JobOrder)).first()
        if existing:
            print("Data already exists, skipping initial seed.")
            return
        print("Entered prod environment.")
        SQLModel.metadata.create_all(engine)
        print("Created tables.")
        seed_users_from_csv()
        print("Seeded users.")
        seed_service_types_from_csv()
        print("Seeded service types.")
        seed_extra_types_from_csv()
        print("Seeded extra types.")
        