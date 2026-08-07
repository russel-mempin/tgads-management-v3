import os

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()
DATABASE_URL = os.getenv("DB_PATH")

engine = create_engine(DATABASE_URL) # type: ignore

def get_session():
    with Session(engine) as session:
        yield session