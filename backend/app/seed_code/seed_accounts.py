from datetime import UTC, datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.database import engine
from app.enums import AccountType
from app.models import Account


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
                beginning_balance=Decimal(118642),
                beginning_balance_date=datetime(2026, 4, 1, 0, 0, 0, tzinfo=UTC),
                current_balance=Decimal(0),
            ),
            Account(
                name="GCash",
                type=AccountType.EWALLET,
                beginning_balance=Decimal("46140.84"),
                beginning_balance_date=datetime(2026, 4, 1, 0, 0, 0, tzinfo=UTC),
                current_balance=Decimal(0),
            ),
            Account(
                name="RCBC (Cheque)",
                type=AccountType.BANK,
                beginning_balance=Decimal("880685.70"),
                beginning_balance_date=datetime(2026, 4, 1, 0, 0, 0, tzinfo=UTC),
                current_balance=Decimal(0),
            ),
        ]

        for account in accounts:
            session.add(account)
        session.commit()