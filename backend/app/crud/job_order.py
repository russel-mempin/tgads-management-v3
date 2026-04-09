from sqlmodel import Session, select
from app.models import JobOrder, JobItem
from sqlalchemy.orm import selectinload

def get_all_job_orders(
    db: Session, offset: int = 0, limit: int = 100
) -> list[JobOrder]:
    job_orders = list(db.exec(
        select(JobOrder).offset(offset)
        .limit(limit)
    ).all())
    return job_orders