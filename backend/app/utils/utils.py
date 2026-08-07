from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from app.enums import PriceUnit, PricingStrategy, SizeUnit
from app.models import Service, ServiceOption, User
from app.schemas.job_order import PricingData

PRICE_UNIT_TO_SIZE_UNIT = {
    PriceUnit.SQIN: SizeUnit.INCHES,
    PriceUnit.SQFT: SizeUnit.FEET,
    PriceUnit.SQM: SizeUnit.METER,
}

AREA_TO_SQIN = {
    SizeUnit.INCHES: 1,
    SizeUnit.FEET: 144,
    SizeUnit.METER: 1 / 0.00064516,
    SizeUnit.CENTIMETER: 1 / 6.4516,
    SizeUnit.MILLIMETER: 1 / 645.16,
}

MANILA = ZoneInfo("Asia/Manila")

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
    

def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=MANILA)

    return dt.astimezone(UTC)


def to_local(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt

    return dt.astimezone(MANILA).replace(tzinfo=None)


def get_system_admin(session: Session) -> User:
    sysadmin = session.exec(
		select(User).where(User.username == "system.admin")
	).first()
    
    if sysadmin is None:
        raise ValueError(
			"System admin user not found. Please seed users first."
		)
        
    return sysadmin
    
    
def compute_unit_price(height: float | None, width: float | None, service_type: Service, option: ServiceOption, size_unit: SizeUnit | None, quantity: int) -> PricingData:
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
		try:
			area_in2 = height * width * AREA_TO_SQIN[size_unit]
		except KeyError:
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
		billable_area = area_conversions[needed_unit]
		consumption = billable_area * quantity
  
		# Determine tier
		tiers = sorted(
			[t for t in option.price_tiers if t.min_threshold is not None],
			key=lambda t: t.min_threshold
		)
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
		return PricingData(consumption=round(consumption, 4), consumption_unit=service_type.unit, rate=round(rate, 2), unit_price=round(billable_area * rate, 2))
	else:
		# For Fixed Pricing (Desktop Printing, Digital Print, Riso)
		return PricingData(consumption=quantity, rate=option.base_rate, unit_price=option.base_rate)