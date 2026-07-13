import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import Service, ServiceOption, ServicePriceTier
from app.enums import PricingStrategy, PriceUnit
from app.utils.utils import to_float
 
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SERVICES_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "services.csv")
SERVICE_OPTIONS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "service_options.csv")
SERVICE_PRICE_TIERS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "service_price_tiers.csv")
 
 
def parse_enum(enum_cls, raw: str):
    """Match a CSV value against an enum's value, e.g. 'Area' -> PricingStrategy.AREA."""
    for member in enum_cls:
        if raw.strip().lower() == member.value.lower():
            return member
    raise ValueError(f"'{raw}' is not a valid {enum_cls.__name__}")
 
 
def seed_services_from_csv(file_path: str = SERVICES_CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
 
        for row in reader:
            existing = session.exec(
                select(Service).where(Service.name == row["name"])
            ).first()
 
            if existing:
                continue
 
            service = Service(
                name=row["name"],
                abbreviation=row["abbreviation"],
                pricing_strategy=parse_enum(PricingStrategy, row["pricing_strategy"]),
                unit=parse_enum(PriceUnit, row["unit"]),
                is_active=row["is_active"].strip().lower() in ("true", "1", "yes"),
            )
 
            session.add(service)
 
        session.commit()
 
 
def seed_service_options_from_csv(file_path: str = SERVICE_OPTIONS_CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
 
        for row in reader:
            service = session.exec(
                select(Service).where(Service.name == row["service_name"])
            ).first()
 
            if service is None:
                print(f"[SKIP] No service named '{row['service_name']}' "
                      f"for option '{row['option_name']}' — run seed_services_from_csv first?")
                continue
 
            existing = session.exec(
                select(ServiceOption).where(
                    ServiceOption.service_id == service.id,
                    ServiceOption.name == row["option_name"],
                )
            ).first()
 
            if existing:
                continue
 
            base_rate_raw = row.get("base_rate", "").strip()
 
            option = ServiceOption(
                service_id=service.id,
                name=row["option_name"],
                base_rate=to_float(base_rate_raw) if base_rate_raw else None,
            )
 
            session.add(option)
 
        session.commit()
 
 
def seed_service_price_tiers_from_csv(file_path: str = SERVICE_PRICE_TIERS_CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
 
        for row in reader:
            service = session.exec(
                select(Service).where(Service.name == row["service_name"])
            ).first()
 
            if service is None:
                print(f"[SKIP] No service named '{row['service_name']}' "
                      f"for tier on '{row['option_name']}'")
                continue
 
            option = session.exec(
                select(ServiceOption).where(
                    ServiceOption.service_id == service.id,
                    ServiceOption.name == row["option_name"],
                )
            ).first()
 
            if option is None:
                print(f"[SKIP] No option '{row['option_name']}' under service "
                      f"'{row['service_name']}' — run seed_service_options_from_csv first?")
                continue
 
            min_threshold = to_float(row.get("min_threshold", "").strip() or "0")
            max_threshold_raw = row.get("max_threshold", "").strip()
            max_threshold = to_float(max_threshold_raw) if max_threshold_raw else None
 
            existing = session.exec(
                select(ServicePriceTier).where(
                    ServicePriceTier.service_option_id == option.id,
                    ServicePriceTier.min_threshold == min_threshold,
                    ServicePriceTier.max_threshold == max_threshold,
                )
            ).first()
 
            if existing:
                continue
 
            tier = ServicePriceTier(
                service_option_id=option.id,
                min_threshold=min_threshold,
                max_threshold=max_threshold,
                rate=to_float(row["rate"]),
            )
 
            session.add(tier)
 
        session.commit()
 
 
def seed_services_data():
    seed_services_from_csv()
    seed_service_options_from_csv()
    seed_service_price_tiers_from_csv()