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
    JobItem,
    ExtraService,
    JobItemExtra,
)
from app.enums import PricingStrategy, ReviewEntityType, SizeUnit, PriceUnit, JobStatus
from app.utils.utils import to_float, to_int
from sqlalchemy import event
from uuid import UUID
from app.services.event_listeners import sync_job_order_on_payment_or_item_change

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JOB_ORDERS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_orders.csv")
JOB_ITEMS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_items.csv")


VOID_REASONS = {
    "1": "No physical paper on Job pile",
    "2": "Listed as cancelled(either on paper or JO Summary) and no service info on physical paper",
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
    # This function should convert the value to a standard unit (e.g., meters)
    if source_unit == target_unit:
        return value
    value_in_meters = value * TO_METERS[source_unit]
    return value_in_meters / TO_METERS[target_unit]  # Convert to target unit


def get_computed_unit_price_from_area(
    price_unit: PriceUnit,
    base_rate: float,
    height: float,
    width: float,
    size_unit: SizeUnit,
) -> float:
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
            reason = row["for_review_reason"].strip()

            # If no customer or has customer but has void choice, inserts job data to void table and determines void reason.
            if not customer_name or void_choice:
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
                    session.add(
                        VoidJobOrder(
                            jo_number=jo_number, job_date=date_received, reason=reason, created_by_id=sysadmin.id
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
                overall_job_status=JobStatus.RELEASED,
            )
            session.add(job_order)

            # Then, if marked for review in spreadsheet, mark for review in the database.
            if for_review:
                session.add(
                    ForReview(
                        entity_type=ReviewEntityType.JOB_ORDER,
                        entity_id=job_order.id,
                        entity_reference=row["jo_number"].strip(),
                        reason=reason,
                    )
                )
                print(f"JO {jo_number} has been marked for review.")
        session.commit()


def seed_job_items(file_path: str = JOB_ITEMS_CSV_PATH):
    item_sequence_by_jo_and_abbr: dict[tuple[int, str], int] = {}
    touched_job_order_ids: set[UUID] = set()
    event.remove(Session, "before_flush", sync_job_order_on_payment_or_item_change)
    try:
        with Session(engine) as session, open(file_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # First, determine service and get other info needed for data validation
                cancelled = row["cancelled"].strip().upper() == "TRUE"
                service = session.exec(
                    select(Service).where(Service.name == row["service"].strip())
                ).first()
                if not service:
                    if not cancelled:
                        print(f"Service for Job {row["jo_number"]} {row['service']} not found. Skipping job item.")    
                    continue
                service_requires_size = service.pricing_strategy == PricingStrategy.AREA

                # If any of these are missing, skip. Because they are essential data on most cases.
                jo_number = int(row["jo_number"].strip())
                height = to_float(row["height"].strip()) if service_requires_size else None
                width = to_float(row["width"].strip()) if service_requires_size else None
                size_unit = (
                    SizeUnit(row["unit"].strip()) if row.get("unit", "").strip() else None
                )
                quantity = to_int(row["quantity"].strip())

                # Getting fields from csv that have a use other than insertion
                csv_unit_price = to_float(row["unit_price"].strip())
                extra_service = row["extra_service"].strip()
                extra_quantity = to_int(row["extra_quantity"])
                discount = to_float(row.get("discount", 0.0))
                extra_charge = to_float(row.get("extra_charge", 0.0))

                # Initialize variables for use
                extra_service_price = 0.0
                computed_unit_price = 0.0

                # Dependency checks for job items, find the data that matches from the database and get it. If none, skip and report.
                job_order = session.exec(
                    select(JobOrder).where(JobOrder.jo_number == jo_number)
                ).first()
                if not job_order:
                    if not cancelled:
                        print(f"Job Order {jo_number} not found. Skipping job item.")
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
                extra = session.exec(
                    select(ExtraService).where(ExtraService.name == extra_service)
                ).first()
                if extra:
                    extra_service_price = extra.price

                # Compute pricing and generate item_id before insertion
                if service_requires_size:
                    if height is None or width is None or size_unit is None:
                        print(
                            f"Missing size information for Job Order {jo_number} ({service.name}). Marking for review."
                        )
                        session.add(
                            ForReview(
                                entity_type=ReviewEntityType.JOB_ORDER,
                                entity_id=job_order.id,
                                entity_reference=row["jo_number"].strip(),
                                reason="Missing size information for job item.",
                            )
                        )
                        continue
                    # After validating data, compute unit price and check if the listed price is different
                    # If the computed unit price is different, mark job for review.
                    computed_unit_price = get_computed_unit_price_from_area(
                        price_unit=service.unit,
                        base_rate=option.base_rate,
                        height=height,
                        width=width,
                        size_unit=size_unit,
                    )
                    if (computed_unit_price + extra_service_price) > csv_unit_price:
                        session.add(
                            ForReview(
                                entity_type=ReviewEntityType.JOB_ORDER,
                                entity_id=job_order.id,
                                entity_reference=row["jo_number"].strip(),
                                reason="Possibly undercharged based on system computation and listed unit price from JO Summary excel.",
                            )
                        )
                    elif (computed_unit_price + extra_service_price) < csv_unit_price:
                        session.add(
                            ForReview(
                                entity_type=ReviewEntityType.JOB_ORDER,
                                entity_id=job_order.id,
                                entity_reference=row["jo_number"].strip(),
                                reason="Possibly overcharged based on system computation and listed unit price from JO Summary excel.",
                            )
                        )

                sequence = (
                    item_sequence_by_jo_and_abbr.get((jo_number, service.abbreviation), 0)
                    + 1
                )
                item_sequence_by_jo_and_abbr[(jo_number, service.abbreviation)] = sequence
                if sequence > 999:
                    print(
                        f"JO {jo_number}: more than 999 of '{service.name}. Item_id may be invalid."
                    )
                    continue
                item_id = f"{jo_number}-{service.abbreviation}-{sequence}"

                item = JobItem(
                    item_id=item_id,
                    description=row["description"].strip() or None,
                    height=height,
                    width=width,
                    size_unit=size_unit,
                    quantity=quantity,
                    job_status=JobStatus.CANCELLED if cancelled else JobStatus.RELEASED,
                    due_date=job_order.date_received,
                    notes=None,
                    unit_price=csv_unit_price,
                    discount_amount=discount,
                    extra_charge=extra_charge,
                    subtotal=(csv_unit_price * quantity) - discount + (extra_charge * quantity),
                    service_name_snapshot=service.name,
                    service_option_name_snapshot=option.name,
                    service_abbreviation_snapshot=service.abbreviation,
                    job_order_id=job_order.id,
                    job_order=job_order,
                    service_id=service.id,
                    service_option_id=option.id,
                )

                session.add(item)
                session.flush()
                touched_job_order_ids.add(job_order.id)

                # After inserting the job item, determine extra service (if any) and insert to db
                if extra and extra_quantity > 0:
                    session.add(
                        JobItemExtra(
                            job_item_id=item.id,
                            extra_service_id=extra.id,
                            quantity=extra_quantity,
                            price_snapshot=extra.price,
                            name_snapshot=extra.name,
                        )
                    )
            # Recompute each touched job order exactly once, with the full,
            # final set of items in place.
            for jo_id in touched_job_order_ids:
                jo = session.get(JobOrder, jo_id)
                if jo is not None:
                    jo.sync_computed_fields()
            session.commit()
    finally:
        event.listen(Session, "before_flush", sync_job_order_on_payment_or_item_change)


def seed_job_orders_and_items():
    seed_job_orders()
    seed_job_items()
