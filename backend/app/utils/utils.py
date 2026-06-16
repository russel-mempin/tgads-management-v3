from __future__ import annotations
from typing import TYPE_CHECKING
from sqlmodel import Session
from app.enums import SizeUnit

if TYPE_CHECKING:
    from app.models import ServiceType, JobOrder

def to_float(v: str) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0
    
def to_int(v: str) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0
    
    
def compute_unit_price(height: float, width: float, service_type: ServiceType, size_unit: SizeUnit) -> float:
	if service_type is None:
		return 0.0

	area_in2 = 0.0

	if size_unit == SizeUnit.INCHES:
		area_in2 = height * width
	elif size_unit == SizeUnit.FEET:
		area_in2 = (height * 12) * (width * 12)
	elif size_unit == SizeUnit.CENTIMETER:
		area_in2 = (height * width) / 6.4516
	elif size_unit == SizeUnit.MILLIMETER:
		area_in2 = (height * width) / 645.16

	areas = {
		"sqin": area_in2,
		"sqft": area_in2 / 144,
		"sqm": area_in2 / 1550.0031,
	}

	if not service_type.is_area_based:
		return service_type.price

	unit_key = service_type.unit.strip().rstrip(".")  # "sqft." → "sqft"

	if unit_key not in areas:
		return 0.0

	return areas[unit_key] * service_type.price


def sync_job_order_status(db: Session, job_order: JobOrder) -> None:
    job_order.payment_status = job_order.computed_payment_status
    job_order.overall_job_status = job_order.computed_overall_job_status
    db.add(job_order)