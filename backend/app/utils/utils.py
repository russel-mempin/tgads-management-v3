from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from app.enums import DatePeriod, PriceUnit, PricingStrategy, SizeUnit
from app.models import Service, ServiceOption, User
from app.schemas.job_order import PricingData

PRICE_UNIT_TO_SIZE_UNIT = {
    PriceUnit.SQIN: SizeUnit.INCHES,
    PriceUnit.SQFT: SizeUnit.FEET,
    PriceUnit.SQM: SizeUnit.METER,
}

LENGTH_TO_FEET = {
    SizeUnit.INCHES: 1 / 12,
    SizeUnit.FEET: 1,
    SizeUnit.METER: 3.280839895,
    SizeUnit.CENTIMETER: 1 / 30.48,
    SizeUnit.MILLIMETER: 1 / 304.8,
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
    except TypeError, ValueError:
        return 0


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=MANILA)

    return dt.astimezone(UTC)


def to_local(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt

    return dt.astimezone(MANILA).replace(tzinfo=None)


def parse_currency(value: str) -> float:
    cleaned = (value or "").replace("₱", "").replace(",", "").strip()
    return to_float(cleaned) if cleaned else 0.0


def parse_date(value: str) -> datetime:
    value = value.strip()

    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=UTC)
        except ValueError:
            pass

    raise ValueError(f"Unsupported date format: {value}")


def get_system_admin(session: Session) -> User:
    sysadmin = session.exec(select(User).where(User.username == "system.admin")).first()

    if sysadmin is None:
        raise ValueError("System admin user not found. Please seed users first.")

    return sysadmin


def validate_price_tiers(price_tiers) -> None:
    tiers = sorted(price_tiers, key=lambda t: t.min_threshold)

    for tier in tiers:
        if tier.max_threshold is not None and tier.max_threshold < tier.min_threshold:
            raise ValueError(
                f"Invalid price tier: minimum threshold "
                f"({tier.min_threshold}) cannot be greater than "
                f"maximum threshold ({tier.max_threshold})."
            )

    for i in range(len(tiers) - 1):
        current = tiers[i]
        next_tier = tiers[i + 1]

        if current.max_threshold is None:
            raise ValueError("An open-ended price tier must be the last tier.")

        if next_tier.min_threshold <= current.max_threshold:
            raise ValueError(
                f"Price tiers overlap: "
                f"{current.min_threshold}-{current.max_threshold} and "
                f"{next_tier.min_threshold}-"
                f"{next_tier.max_threshold if next_tier.max_threshold is not None else '∞'}."
            )


def compute_unit_price(
    height: float | None,
    width: float | None,
    service_type: Service,
    option: ServiceOption,
    size_unit: SizeUnit | None,
    quantity: int,
) -> PricingData:
    if service_type is None:
        raise ValueError("Service type cannot be blank.")

    if option is None:
        raise ValueError("Service option/variant cannot be blank.")

    if quantity is None:
        raise ValueError("Quantity cannot be blank.")

    if service_type.pricing_strategy == PricingStrategy.AREA:
        if height is None or width is None or size_unit is None:
            raise ValueError("Dimension data cannot be incomplete.")

        # Apply stock increment to WIDTH.
        # stock_increment is always expressed in feet.
        if option.stock_increment is not None:
            if option.stock_increment <= 0:
                raise ValueError("Stock increment must be greater than zero.")

            width_ft = width * LENGTH_TO_FEET[size_unit]

            width_ft = (
                math.ceil(width_ft / option.stock_increment) * option.stock_increment
            )

            # Convert adjusted width back to the original unit.
            width = width_ft / LENGTH_TO_FEET[size_unit]

        # Calculate area using the adjusted width.
        try:
            area_in2 = height * width * AREA_TO_SQIN[size_unit]
        except KeyError:
            raise ValueError(f"Unsupported size unit: {size_unit}")

        # Convert area to the service's pricing unit.
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

        # Determine applicable price tier.
        tiers = sorted(
            [tier for tier in option.price_tiers if tier.min_threshold is not None],
            key=lambda tier: tier.min_threshold,
        )

        applicable_tier = None

        for tier in tiers:
            if tier.max_threshold is None:
                if consumption >= tier.min_threshold:
                    applicable_tier = tier
                    break

            elif tier.min_threshold <= consumption < tier.max_threshold:
                applicable_tier = tier
                break

        rate = applicable_tier.rate if applicable_tier else option.base_rate

        return PricingData(
            consumption=round(consumption, 4),
            consumption_unit=service_type.unit,
            rate=rate.quantize(Decimal("0.001")),
            unit_price=(Decimal(str(billable_area)) * rate).quantize(Decimal("0.01")),
        )

    # Fixed pricing
    return PricingData(
        consumption=quantity,
        rate=option.base_rate,
        unit_price=option.base_rate,
    )


def get_date_range(period: DatePeriod):
    now = datetime.now(MANILA)

    if period == DatePeriod.TODAY:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif period == DatePeriod.THIS_WEEK:
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=7)
    elif period == DatePeriod.THIS_MONTH:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (
            start.replace(year=start.year + 1, month=1)
            if start.month == 12
            else start.replace(month=start.month + 1)
        )
    elif period == DatePeriod.LAST_MONTH:
        end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start = (
            end.replace(year=end.year - 1, month=12)
            if end.month == 1
            else end.replace(month=end.month - 1)
        )
    elif period == DatePeriod.THIS_YEAR:
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(year=start.year + 1)
    else:
        return None, None

    return start, end
