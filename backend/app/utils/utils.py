from __future__ import annotations
from typing import TYPE_CHECKING
from sqlmodel import Session, select
from app.enums import SizeUnit
from app.models import User

if TYPE_CHECKING:
    from app.models import Service, JobOrder

def to_float(value: str) -> float:
    if not value:
        return 0.0
    cleaned = value.replace("₱", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0
    
def to_int(v: str) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0
    

def get_system_admin(session: Session) -> User:
    sysadmin = session.exec(
		select(User).where(User.username == "system.admin")
	).first()
    
    if sysadmin is None:
        raise ValueError(
			"System admin user not found. Please seed users first."
		)
        
    return sysadmin
    
    
def compute_unit_price(height: float, width: float, service_type: Service, size_unit: SizeUnit) -> float:
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