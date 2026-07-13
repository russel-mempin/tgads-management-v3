import os
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine
from app.services.event_listeners import sync_job_order_on_payment_or_item_change

load_dotenv()
DATABASE_URL = os.getenv("DB_PATH")

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session