import csv
import os
from sqlmodel import Session, select
from app.database import engine
from datetime import datetime, timezone
from app.models import (
    User,
    Customer,
    VoidJobOrder,
    JobOrder,
    ForReview,
    Service,
    ServiceOption,
)
from app.enums import PricingStrategy, ReviewEntityType, SizeUnit, PriceUnit
from app.utils.utils import to_float

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JOB_ORDERS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_orders.csv")
JOB_ITEMS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_items.csv")


VOID_REASONS = {
    "1": "No physical paper on Job pile",
    "2": "Listed as cancelled",
    "3": "Duplicate",
    "4": "Conflicting info on job summary excel and physical paper",
    "5": "Other",
}
TO_METERS = {
    SizeUnit.MILLIMETER: 0.001,
    SizeUnit.CENTIMETER: 0.01,
    SizeUnit.METER: 1.0,
    SizeUnit.INCHES: 0.0254,
    SizeUnit.FEET: 0.3048,
}
PRICE_UNIT_TO_SIZE_UNIT = {
    PriceUnit.SQIN: SizeUnit.INCHES,
    PriceUnit.SQFT: SizeUnit.FEET,
    PriceUnit.SQM: SizeUnit.METER,
}


# Helper functions
def parse_date(value: str) -> datetime:
    dt = datetime.strptime(value.strip(), "%m/%d/%y")
    return dt.replace(tzinfo=timezone.utc)


def get_or_create_customer(session: Session, customer_name: str) -> Customer:
    customer_name = customer_name.strip()
    existing = session.exec(
        select(Customer).where(Customer.name == customer_name)
    ).first()
    if existing:
        return existing
    customer = Customer(name=customer_name)
    session.add(customer)
    session.flush()
    return customer


def unit_converter(source_unit: SizeUnit, value: float, target_unit: SizeUnit) -> float:
    # Placeholder for actual unit conversion logic
    # This function should convert the value to a standard unit (e.g., meters)
    if source_unit == target_unit:
        return value
    value_in_meters = value * TO_METERS[source_unit]
    return value_in_meters / TO_METERS[target_unit]  # Convert to target unit


def get_computed_unit_price_from_area(price_unit: PriceUnit, base_rate: float, height: float, width: float, size_unit: SizeUnit) -> float:
    # Placeholder for actual logic to compute unit price
    # Only use if the service's pricing strategy is "Area"
    # Convert height and width to appropriate unit based on unit from Service
    # Then, compute for the area and multiply by the base_rate from ServiceOption
    try:
        target_size_unit = PRICE_UNIT_TO_SIZE_UNIT[price_unit]
    except KeyError:
        raise ValueError(f"Unsupported price unit: {price_unit}")
    converted_height = unit_converter(
        value=height,
        source_unit=size_unit,
        target_unit=target_size_unit,
    )
    converted_width = unit_converter(
        value=width,
        source_unit=size_unit,
        target_unit=target_size_unit,
    )
    area = converted_height * converted_width
    return area * base_rate


def seed_job_orders(file_path: str = JOB_ORDERS_CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        sysadmin = session.exec(
            select(User).where(User.username == "system.admin")
        ).first()
        if not sysadmin:
            raise ValueError("System admin user not found. Please seed users first.")
        for row in reader:
            date_received = parse_date(row["date"])
            jo_number = int(row["jo_number"].strip())
            customer_name = (row["customer_name"] or "").strip()
            void_choice = row["void_choice"].strip()
            for_review = row["for_review"].strip().lower()

            # If no customer, inserts job data to void table and determines void reason.
            if not customer_name:
                existing_in_void = session.exec(
                    select(VoidJobOrder).where(VoidJobOrder.jo_number == jo_number)
                ).first()
                if not existing_in_void:
                    # If and elif block could be deleted for automation
                    if void_choice:
                        # Determine reason here
                        reason = VOID_REASONS[void_choice]
                        print(
                            f"JO {jo_number} has been inserted to void job orders table."
                        )
                    else:
                        while True:
                            print(
                                f"\n JO #{jo_number} has no customer name. This would be inserted in the Void Job Orders table."
                            )
                            print("\n Select a reason:")

                            for key, value in VOID_REASONS.items():
                                print(f"[{key}] {value}")

                            choice = input("> ").strip()

                            if choice in VOID_REASONS:
                                if choice == "5":
                                    reason = input("Enter custom reason: ").strip()
                                else:
                                    reason = VOID_REASONS[choice]
                                break
                            print("Invalid choice. Try again.")
                    session.add(
                        VoidJobOrder(
                            jo_number=jo_number, job_date=date_received, reason=reason
                        )
                    )
                    session.commit()
                    continue

            # Else, determine customer and insert job order data to job orders table
            customer = get_or_create_customer(session, customer_name)
            job_order = JobOrder(
                date_received=date_received,
                jo_number=jo_number,
                customer_id=customer.id,
                created_by_id=sysadmin.id,
                updated_by_id=sysadmin.id,
            )
            session.add(job_order)

            # Then, if marked for review in spreadsheet, mark for review in the database.
            if for_review:
                session.add(
                    ForReview(
                        entity_type=ReviewEntityType.JOB_ORDER,
                        entity_id=job_order.id,
                        reason="Marked for review in spreadsheet (Make column in spreadsheet for accuracy.)",
                    )
                )
                print(f"JO {jo_number} has been marked for review.")
            session.commit()


def seed_job_items(file_path: str = JOB_ITEMS_CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jo_number = int(row["jo_number"].strip())

            job_order = session.exec(
                select(JobOrder).where(JobOrder.jo_number == jo_number)
            ).first()
            if not job_order:
                print(f"Job Order {jo_number} not found. Skipping job item.")
                continue

            service = session.exec(
                select(Service).where(Service.name == row["service"].strip())
            ).first()
            if not service:
                print(f"Service {row['service']} not found. Skipping job item.")
                continue

            option = session.exec(
                select(ServiceOption).where(
                    ServiceOption.service_id == service.id,
                    ServiceOption.name == row["option"].strip(),
                )
            ).first()
            if option is None:
                print(
                    f"Service Option {row['option']} for Service {service.name} not found. Skipping job item."
                )
                continue

            service_requires_size = service.pricing_strategy == PricingStrategy.AREA
            height = to_float(row["height"]) if service_requires_size else None
            width = to_float(row["width"]) if service_requires_size else None
            size_unit = SizeUnit(row["size_unit"]) if service_requires_size else None

            if service_requires_size:
                if height is None or width is None or size_unit is None:
                    print(
                        f"Missing size information for Job Order {jo_number} ({service.name}). Marking for review."
                    )
                    session.add(
                        ForReview(
                            entity_type=ReviewEntityType.JOB_ORDER,
                            entity_id=job_order.id,
                            reason="Missing size information for job item.",
                        )
                    )
                    continue
                # After validating data, compute unit price and check if the listed price is different
                # If the computed unit price is different, input the difference as discount and mark job for review.
                computed_unit_price = get_computed_unit_price_from_area(
                    price_unit=service.unit,
                    base_rate=option.base_rate,
                    height=height,
                    width=width,
                    size_unit=size_unit
                )