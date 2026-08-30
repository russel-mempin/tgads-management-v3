import uuid

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models import ExtraService, JobItem, JobItemExtra, ServiceOption
from app.schemas.job_order import JobItemCreate, JobItemExtraCreate
from app.utils.utils import compute_unit_price


def _get_service_data_from_option(db: Session, option_id: uuid.UUID):
    option = db.get(ServiceOption, option_id)
    if not option:
        raise HTTPException(status_code=404, detail="Variant not found.")
    service = option.service
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")
    return option, service


def get_extra_service_data_by_id(db: Session, extra_id: uuid.UUID):
    extra = db.get(ExtraService, extra_id)
    if not extra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extra service not found.")
    return extra


def build_job_item(
    db: Session,
    job_order_id: uuid.UUID,
    data: JobItemCreate,
    extras: list[tuple[JobItemExtraCreate, ExtraService]],
) -> JobItem:
    option, service = _get_service_data_from_option(db, data.service_option_id)
    pricing_data = compute_unit_price(
        data.height, data.width, service, option, data.size_unit, data.quantity
    )
    extra_total = sum(
        extra_service.price * extra.quantity for extra, extra_service in extras
    )
    subtotal = round(
        (pricing_data.unit_price * data.quantity)
        + extra_total
        + (data.extra_charge * data.quantity)
        - data.discount_amount,
        2,
    )
    return JobItem(
        description=data.description,
        discount_amount=data.discount_amount,
        due_date=data.due_date,
        extra_charge=data.extra_charge,
        height=data.height,
        item_id=data.item_id,
        job_status=data.job_status,
        notes=data.notes,
        quantity=data.quantity,
        service_abbreviation_snapshot=service.abbreviation,
        service_option_name_snapshot=option.name,
        service_name_snapshot=service.name,
        size_unit=data.size_unit,
        subtotal=subtotal,
        unit_price=pricing_data.unit_price,
        width=data.width,
        job_order_id=job_order_id,
        service_id=service.id,
        service_option_id=option.id,
    )


def build_job_item_extra(
    job_item_id: uuid.UUID,
    data: JobItemExtraCreate,
    extra_service: ExtraService,
) -> JobItemExtra:
    return JobItemExtra(
        job_item_id=job_item_id,
        extra_service_id=extra_service.id,
        quantity=data.quantity,
        name_snapshot=extra_service.name,
        price_snapshot=extra_service.price,
    )