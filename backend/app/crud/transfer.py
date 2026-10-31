from sqlmodel import Session, select

from app.models import AccountTransfer
from app.schemas.transfer import AccountTransferPublic


def get_all_transfers(db: Session, include_archived: bool = False, search: str | None = None) -> list[AccountTransferPublic]:
    statement = select(AccountTransfer)

    if not include_archived:
        statement = statement.where(AccountTransfer.is_archived.is_(False))

    if search:
        statement = statement.where(
            AccountTransfer.description.ilike(f"%{search}%")
        )
    
    statement = statement.order_by(AccountTransfer.transferred_at.desc())
    print(statement)
    return list(db.exec(statement).all())