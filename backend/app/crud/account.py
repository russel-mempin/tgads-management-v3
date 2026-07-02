from sqlmodel import Session, select
from app.models import Account
from app.schemas.account import AccountOption


def get_all_account_names(
    db: Session, offset: int = 0, limit: int = 100
) -> list[AccountOption]:
    accounts = list(db.exec(
        select(Account).offset(offset).limit(limit)
    ).all())
    return [AccountOption(id=a.id, name=a.name) for a in accounts]