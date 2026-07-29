from __future__ import annotations

from sqlmodel import Session, select

from app.enums import PriceUnit, PricingStrategy, SizeUnit
from app.models import Service, ServiceOption, User

PRICE_UNIT_TO_SIZE_UNIT = {
    PriceUnit.SQIN: SizeUnit.INCHES,
    PriceUnit.SQFT: SizeUnit.FEET,
    PriceUnit.SQM: SizeUnit.METER,
}

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
    
    
def compute_unit_price(height: float, width: float, service_type: Service, option: ServiceOption, size_unit: SizeUnit, quantity: int) -> float:
	if service_type is None:
		raise ValueError("Service type cannot be blank.")
	if option is None:
		raise ValueError("Service option/variant cannot be blank.")
	if quantity is None:
		raise ValueError("Quantity cannot be blank.")

	if service_type.pricing_strategy == PricingStrategy.AREA:
		if height is None or width is None or size_unit is None:
			raise ValueError("Dimension data cannot be incomplete.")
		
		# Convert to square inches first as base unit
		if size_unit == SizeUnit.INCHES:
			area_in2 = height * width
		elif size_unit == SizeUnit.FEET:
			area_in2 = (height * 12) * (width * 12)
		elif size_unit == SizeUnit.METER:
			area_in2 = (height * width) / 0.00064516
		else:
			raise ValueError(f"Unsupported size unit: {size_unit}")

		# Convert to the unit the service needs for pricing
		area_conversions = {
            PriceUnit.SQIN: area_in2,
            PriceUnit.SQFT: area_in2 / 144,
            PriceUnit.SQM: area_in2 / 1550.0031,
        }
  
		needed_unit = service_type.unit
		if needed_unit not in area_conversions:
			raise ValueError(f"Unsupported price unit: {needed_unit}")
		area = area_conversions[needed_unit]
		consumption = area * quantity
  
		# Determine tier
		tiers = sorted(
			[t for t in option.price_tiers if t.min_threshold is not None],
			key=lambda t: t.min_threshold
		)
		print(f"consumption: {consumption}")
		applicable_tier = None
		for tier in tiers:
			if tier.max_threshold is None:
				if consumption >= tier.min_threshold:
					applicable_tier = tier
					break
			else:
				if tier.min_threshold <= consumption < tier.max_threshold:
					applicable_tier = tier
					break
		if applicable_tier:
			rate = applicable_tier.rate
		else:
			rate = option.base_rate
		return area * rate
	else:
		return option.base_rate * quantity