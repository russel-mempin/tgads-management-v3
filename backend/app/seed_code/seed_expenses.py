import csv
import os
from decimal import Decimal

from sqlmodel import Session, select

from app.database import engine
from app.enums import ExpenseCategory
from app.models import Account, AccountTransaction, Expense
from app.utils.utils import parse_date

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "2026expenses.csv")

def seed_expenses_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        METHOD_TO_ACCOUNT = {
            "Cash": "Cash",
            "GCash": "GCash",
            "Cheque": "RCBC",
        }
        
        for row in reader:
            account_name = METHOD_TO_ACCOUNT.get(row["method"])
            if not account_name:
                raise ValueError(f"No account mapped for method: {row['method']}")
            account = session.exec(
                select(Account).where(Account.name == account_name)
            ).first()
            if not account:
                raise ValueError(f"Account '{account_name}' not found in database")
            date = parse_date(row['date'])
            expense = Expense(
                date=date,
                category=ExpenseCategory(row["category"]),
                description=row["description"],
                amount=Decimal(row["amount"].replace(",", "").strip()),
                account_id=account.id,
                account_name_snapshot=account.name
            )
            session.add(expense)
            
            current_balance = account.current_balance
            new_balance = current_balance - expense.amount

            transaction = AccountTransaction(
                account_id=account.id,
                date=date,
                description=row["description"],
                amount=-expense.amount,
                running_balance=new_balance,
                source_type="expense",
                source_id=expense.id,
            )

            session.add(transaction)
            session.commit()
        session.commit()