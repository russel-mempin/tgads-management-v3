from __future__ import annotations
from typing import TYPE_CHECKING

from app.enums import SizeUnit

if TYPE_CHECKING:
    from app.models import ServiceType

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
    
def compute_unit_price(height: float, width: float, service_type: ServiceType) -> float:
    area_in2 = 0.0

    if service_type.required_measurement_unit == SizeUnit.INCHES:
        area_in2 = height * width

    elif service_type.required_measurement_unit == SizeUnit.FEET:
        area_in2 = (height * 12) * (width * 12)

    elif service_type.required_measurement_unit == SizeUnit.CENTIMETER:
        area_in2 = (height * width) / 6.4516

    areas = {
        "sqin": area_in2,
        "sqft": area_in2 / 144,
        "sqm": area_in2 / 1550.0031,
    }

    if service_type is None:
        return 0.0

    if not service_type.is_area_based:
        return service_type.price

    if service_type.unit not in areas:
        return 0.0

    return areas[service_type.unit] * service_type.price