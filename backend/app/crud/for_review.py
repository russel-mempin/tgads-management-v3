from sqlmodel import Session, select
from app.models import ForReview


def get_all_for_review_items(
    db: Session, offset: int = 0, limit: int = 100
) -> list[ForReview]:
    return list(db.exec(select(ForReview).offset(offset).limit(limit)).all())
