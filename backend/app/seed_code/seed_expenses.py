import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import Expense, Account, AccountTransaction
from app.enums import ExpenseCategory
from app.utils.utils import to_float
from datetime import datetime

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
            account_name = METHOD_TO_ACCOUNT.get(row["Method"])
            if not account_name:
                raise ValueError(f"No account mapped for method: {row['Method']}")
            account = session.exec(
                select(Account).where(Account.name == account_name)
            ).first()
            if not account:
                raise ValueError(f"Account '{account_name}' not found in database")
            expense = Expense(
                date=datetime.strptime(f"{row['Date']} 2026", "%d-%b %Y"),
                category=ExpenseCategory(row["Category"]),
                description=row["Description"],
                amount=to_float(row["OUT"]),
                account_id=account.id
            )
            session.add(expense)
            
            new_balance = account.current_balance - expense.amount
            account.current_balance = new_balance
            session.add(account)
            transaction = AccountTransaction(
                account_id=account.id,
                date=datetime.strptime(f"{row['Date']} 2026", "%d-%b %Y"),
                description=row["Description"],
                amount=expense.amount,
                running_balance=new_balance,
                source_type="expense",
                source_id=expense.id,
            )
            session.add(transaction)
            session.commit()
        session.commit()