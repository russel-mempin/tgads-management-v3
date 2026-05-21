import os
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel
from app.database import engine
from app.seed_code.seed_users import seed_users_from_csv
from app.seed_code.seed_service_types import seed_service_types_from_csv
from app.seed_code.seed_extra_types import seed_extra_types_from_csv
from app.seed_code.seed_customers import seed_customers_from_csv
from app.seed_code.seed_job_orders import seed_job_orders_from_csv
from app.seed_code.seed_job_items import seed_job_items_from_csv
from app.seed_code.seed_payments import seed_payments_from_csv
from app.seed_code.seed_claiming_history import seed_claiming_history_from_csv

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
        SQLModel.metadata.create_all(engine)
        print("Created all tables without data.")
        return

    with Session(engine) as session:
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
        seed_job_orders_from_csv()
        print("Seeded job orders.")
        seed_job_items_from_csv()
        print("Seeded job items.")
        seed_payments_from_csv()
        print("Seeded payments.")
        seed_claiming_history_from_csv()
        print("Seeded claiming history.")