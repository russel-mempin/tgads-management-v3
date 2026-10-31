import csv
import os
from decimal import Decimal

from sqlmodel import Session, select

from app.database import engine
from app.enums import TransactionSource
from app.models import Account, AccountTransaction, MiscSale, User
from app.utils.utils import parse_date

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "misc_sales.csv")

def seed_misc_sales_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        METHOD_TO_ACCOUNT = {
            "Cash": "Cash",
            "GCash": "GCash",
            "RCBC Old": "RCBC Old",
            "RCBC New": "RCBC New"
        }
        
        for row in reader:
            account_name = METHOD_TO_ACCOUNT.get(row["account_name_snapshot"])
            if not account_name:
                raise ValueError(f"No account mapped for method: {row['account_name_snapshot']}")
            account = session.exec(
                select(Account).where(Account.name == account_name)
            ).first()
            if not account:
                raise ValueError(f"Account '{account_name}' not found in database")
            user = session.exec(
                select(User).where(
                    (User.first_name + " " + User.last_name) == row["created_by_name"]
                )
            ).first()
            if not user:
                raise ValueError(f"User named '{row["created_by_name"]}' not found in database.")
            date = parse_date(row['date'])
            misc_sale = MiscSale(
                date=date,
                description=row["description"],
                amount=Decimal(row["amount"].replace(",", "").strip()),
                account_id=account.id,
                account_name_snapshot=account.name,
                created_by_id=user.id,
                updated_by_id=user.id
            )
            session.add(misc_sale)

            transaction = AccountTransaction(
                account_id=account.id,
                date=date,
                description=row["description"],
                amount=misc_sale.amount,
                source_type=TransactionSource.MISC_SALE,
                source_id=misc_sale.id,
            )

            session.add(transaction)
            session.commit()
        session.commit()