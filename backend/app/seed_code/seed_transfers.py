import csv
import os
from decimal import Decimal

from sqlmodel import Session, select

from app.database import engine
from app.enums import TransactionSource
from app.models import Account, AccountTransaction, AccountTransfer
from app.utils.utils import get_system_admin, parse_date

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "transfers.csv")

def seed_transfers_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        sysadmin = get_system_admin(session)
        reader = csv.DictReader(f)
        METHOD_TO_ACCOUNT = {
            "Cash": "Cash",
            "GCash": "GCash",
            "RCBC Old": "RCBC Old",
            "RCBC New": "RCBC New",
        }
        
        for row in reader:
            source_account_name = METHOD_TO_ACCOUNT.get(row["source"])
            if not source_account_name:
                raise ValueError(f"No account mapped for source: {row['source']}")
            source_account = session.exec(
                select(Account).where(Account.name == source_account_name)
            ).first()
            if not source_account:
                raise ValueError(f"Account '{source_account_name}' not found in database")
            destination_account_name = METHOD_TO_ACCOUNT.get(row["destination"])
            if not destination_account_name:
                raise ValueError(f"No account mapped for destination: {row['destination']}")
            destination_account = session.exec(
                select(Account).where(Account.name == destination_account_name)
            ).first()
            if not source_account:
                raise ValueError(f"Account '{destination_account_name}' not found in database")
            date = parse_date(row['transferred_at'])
            transfer = AccountTransfer(
                reference_number=row["reference_number"],
                description=row["description"],
                amount=Decimal(row["amount"].replace(",", "").strip()),
                transferred_at=date,
                source_account_id=source_account.id,
                destination_account_id=destination_account.id,
                created_by_id=sysadmin.id,
                updated_by_id=sysadmin.id
            )
            session.add(transfer)

            source_transaction = AccountTransaction(
                account_id=source_account.id,
                date=date,
                description=row["description"],
                amount=-transfer.amount,
                source_type=TransactionSource.TRANSFER_SOURCE,
                source_id=transfer.id,
            )
            session.add(source_transaction)

            destination_transaction = AccountTransaction(
                account_id=destination_account.id,
                date=date,
                description=row["description"],
                amount=transfer.amount,
                source_type=TransactionSource.TRANSFER_DESTINATION,
                source_id=transfer.id,
            )
            session.add(destination_transaction)
            session.commit()
        session.commit()