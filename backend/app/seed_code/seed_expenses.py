import csv, os
from sqlmodel import Session
from app.database import engine
from app.models import Expense
from app.enums import ExpenseCategory
from app.utils.utils import to_float
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "2026expenses.csv")

def seed_expenses_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            expense = Expense(
                date=datetime.strptime(f"{row['Date']} 2026", "%d-%b %Y"),
                category=ExpenseCategory(row["Category"]),
                description=row["Description"],
                amount=to_float(row["OUT"]),
            )
            session.add(expense)
        session.commit()