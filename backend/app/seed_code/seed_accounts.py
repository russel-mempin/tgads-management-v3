from sqlmodel import Session, select
from app.database import engine
from app.models import Account
from app.enums import AccountType
from datetime import datetime, timezone

def seed_accounts():
    with Session(engine) as session:
        existing = session.exec(select(Account)).first()
        if existing:
            print("Accounts already seeded, skipping.")
            return

        accounts = [
            Account(
                name="Cash",
                type=AccountType.CASH_ON_HAND,
                beginning_balance=118642,
                beginning_balance_date=datetime(2026, 4, 1, 0, 0, 0, tzinfo=timezone.utc),
                current_balance=0.0,
            ),
            Account(
                name="GCash",
                type=AccountType.EWALLET,
                beginning_balance=46140.84,
                beginning_balance_date=datetime(2026, 4, 1, 0, 0, 0, tzinfo=timezone.utc),
                current_balance=0.0,
            ),
            Account(
                name="RCBC",
                type=AccountType.BANK,
                beginning_balance=880685.70,
                beginning_balance_date=datetime(2026, 4, 1, 0, 0, 0, tzinfo=timezone.utc),
                current_balance=0.0,
            ),
        ]

        for account in accounts:
            session.add(account)
        session.commit()