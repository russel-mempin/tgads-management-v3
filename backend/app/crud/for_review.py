from sqlmodel import Session, select, col
from app.models import ForReview
from sqlalchemy import func


def get_all_for_review_items(
    db: Session, offset: int = 0, limit: int = 100
) -> list[ForReview]:
    return list(db.exec(select(ForReview).offset(offset).limit(limit)).all())


def get_count_of_for_reviews(db: Session) -> int:
    return db.exec(
        select(func.count()).select_from(ForReview).where(
            col(ForReview.resolved_at).is_(None)
        )
    ).one()