from sqlalchemy import event
from sqlmodel import Session
from app.models import Payment, JobItem, JobOrder


def _touched_job_order_ids(session: Session):
    touched = set()

    for obj in list(session.new) + list(session.dirty) + list(session.deleted):
        if not isinstance(obj, (Payment, JobItem)):
            continue

        if obj.job_order_id is not None:
            touched.add(obj.job_order_id)
        elif obj.job_order is not None:
            touched.add(obj.job_order.id)

    return touched


@event.listens_for(Session, "before_flush")
def sync_job_order_on_payment_or_item_change(session, flush_context, instances):
    touched_ids = _touched_job_order_ids(session)
    for job_order_id in touched_ids:
        job_order = session.get(JobOrder, job_order_id)
        if job_order is not None:
            job_order.sync_computed_fields()