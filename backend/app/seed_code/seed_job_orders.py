import csv
import os
from sqlmodel import Session, select, func
from app.database import engine
from app.models import (
    Service,
    ServiceOption,
    Customer,
    JobOrder,
    JobItem,
    ExtraService,
    JobItemExtra,
    VoidJobOrder,
)
from datetime import datetime, timezone
from app.enums import SizeUnit, JobStatus, PricingStrategy
from app.utils.utils import to_float, to_int

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JOB_ORDERS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_orders.csv")
JOB_ITEMS_CSV_PATH = os.path.join(BASE_DIR, "seed_data", "job_items.csv")


def parse_currency(value: str) -> float:
    cleaned = (value or "").replace("₱", "").replace(",", "").strip()
    return to_float(cleaned) if cleaned else 0.0


def parse_date(value: str) -> datetime:
    dt = datetime.strptime(value.strip(), "%m/%d/%y")
    return dt.replace(tzinfo=timezone.utc)


def parse_bool(value: str) -> bool:
    return (value or "").strip().lower() in ("TRUE", "1", "yes", "y")


def get_or_create_customer(session: Session, name: str) -> Customer:
    name = name.strip()
    existing = session.exec(select(Customer).where(Customer.name == name)).first()
    if existing:
        return existing
    customer = Customer(name=name)
    session.add(customer)
    session.flush()
    return customer


def seed_job_orders_from_csv(file_path: str = JOB_ORDERS_CSV_PATH) -> dict[str, int]:
    """Returns a map of {temporary label -> assigned negative jo_number}
    for any row that had no real JO number, so seed_job_items_from_csv can
    resolve the matching rows in the items sheet."""
    unlogged_labels: dict[str, int] = {}
    with Session(engine) as session, open(file_path, newline="") as f:
        lowest_existing = session.exec(select(func.min(JobOrder.jo_number))).first()
        next_unlogged = min(lowest_existing or 0, 0) - 1
        reader = csv.DictReader(f)
        for row in reader:
            customer_name = row["customer_name"].strip()
            jo_number_raw = row["jo_number"].strip()
            date_received = parse_date(row["date"])

            if customer_name.lower() == "cancelled":
                if jo_number_raw:
                    existing_void = session.exec(
                        select(VoidJobOrder).where(
                            VoidJobOrder.jo_number == int(jo_number_raw)
                        )
                    ).first()
                    if not existing_void:
                        session.add(
                            VoidJobOrder(
                                jo_number=int(jo_number_raw),
                                date=date_received,
                                reason="Cancelled - Past data imported",
                            )
                        )
                continue

            is_unlogged = not jo_number_raw.isdigit()
            if is_unlogged:
                jo_number = next_unlogged
                label = jo_number_raw or f"row-{date_received.date()}-{customer_name}"
                unlogged_labels[label] = jo_number
                next_unlogged -= 1
            else:
                jo_number = int(jo_number_raw)
                existing = session.exec(
                    select(JobOrder).where(JobOrder.jo_number == jo_number)
                ).first()
                if existing:
                    continue

            customer = get_or_create_customer(session, customer_name)

            job_order = JobOrder(
                jo_number=jo_number,
                is_unlogged=is_unlogged,
                date_received=date_received,
                customer_id=customer.id,
                for_review=(row.get("for_review", "").strip() or None)
                or (f"Unlogged — sheet label: {label}" if is_unlogged else None),
                overall_job_status=JobStatus.RELEASED,
            )
            session.add(job_order)

        session.commit()
    return unlogged_labels


def seed_job_items_from_csv(
    file_path: str = JOB_ITEMS_CSV_PATH,
    unlogged_labels: dict[str, int] | None = None,
):
    unlogged_labels = unlogged_labels or {}
    skipped: list[str] = []
    item_seq_by_jo_and_abbr: dict[tuple[int, str], int] = {}

    with Session(engine) as session:
        with open(file_path, newline="") as f:
            for row in csv.DictReader(f):
                jo_number_raw = row["jo_number"].strip()

                if jo_number_raw.isdigit():
                    jo_number = int(jo_number_raw)
                elif jo_number_raw in unlogged_labels:
                    jo_number = unlogged_labels[jo_number_raw]
                else:
                    skipped.append(
                        f"'{jo_number_raw}': not a real JO number and not "
                        f"found in unlogged_labels — check for a typo"
                    )
                    continue

                job_order = session.exec(
                    select(JobOrder).where(JobOrder.jo_number == jo_number)
                ).first()
                if job_order is None:
                    skipped.append(
                        f"JO {jo_number}: no matching JobOrder "
                        f"(Check if it is cancelled.)"
                    )
                    continue

                service = session.exec(
                    select(Service).where(Service.name == row["service"].strip())
                ).first()
                if service is None:
                    skipped.append(
                        f"Voided job {jo_number}: no service listed."
                    )
                    void = VoidJobOrder(
                        jo_number=jo_number,
                        date=datetime.now(timezone.utc),
                        reason="Imported from file, listed as cancelled.",
                    )
                    session.add(void)
                    continue
                option = session.exec(
                    select(ServiceOption).where(
                        ServiceOption.service_id == service.id,
                        ServiceOption.name == row["option"].strip(),
                    )
                ).first()
                if option is None:
                    skipped.append(
                        f"JO {jo_number}: no option '{row['option']}' under '{row['service']}'"
                    )
                    continue

                requires_size = service.pricing_strategy == PricingStrategy.AREA
                has_size = not requires_size or (
                    row.get("width", "").strip()
                    and row.get("height", "").strip()
                    and row.get("unit", "").strip()
                )
                has_price = row.get("unit_price", "").strip()

                width = to_float(row["width"]) if row.get("width", "").strip() else None
                height = (
                    to_float(row["height"]) if row.get("height", "").strip() else None
                )
                size_unit = (
                    SizeUnit(row["unit"].strip())
                    if row.get("unit", "").strip()
                    else None
                )
                quantity = (
                    to_int(row["quantity"]) if row.get("quantity", "").strip() else 1
                )
                unit_price = (
                    parse_currency(row.get("unit_price", "")) if has_price else 0.0
                )
                discount = parse_currency(row.get("discount", ""))
                extra_charge = parse_currency(row.get("extra_charge", ""))
                subtotal = (unit_price * quantity) - discount + extra_charge

                cancelled = parse_bool(row.get("cancelled", ""))

                seq = (
                    item_seq_by_jo_and_abbr.get((jo_number, service.abbreviation), 0)
                    + 1
                )
                item_seq_by_jo_and_abbr[(jo_number, service.abbreviation)] = seq
                if seq > 999:
                    skipped.append(
                        f"JO {jo_number}: more than 999 '{service.abbreviation}' "
                        f"items — item_id format can't hold seq={seq}"
                    )
                    continue
                item_id = f"{jo_number}-{service.abbreviation}-{seq}"

                notes = None
                if not (has_size and has_price):
                    skipped.append(
                        f"JO {jo_number} ({service.name}): missing size/price "
                    )
                    notes = "Missing size/price on original sheet"

                item = JobItem(
                    item_id=item_id,
                    job_order=job_order,
                    service_id=service.id,
                    service_option_id=option.id,
                    description=row.get("description", "").strip() or None,
                    notes=notes,
                    width=width,
                    height=height,
                    size_unit=size_unit,
                    quantity=quantity,
                    job_status=JobStatus.CANCELLED if cancelled else JobStatus.RELEASED,
                    due_date=job_order.date_received,
                    unit_price=unit_price,
                    discount_amount=discount,
                    extra_total=extra_charge,
                    subtotal=subtotal,
                    needs_price_review=not (has_size and has_price),
                    service_name_snapshot=service.name,
                    service_option_name_snapshot=option.name,
                    service_abbreviation_snapshot=service.abbreviation,
                )
                session.add(item)
                session.flush()

                extra_service_name = row.get("extra_service", "").strip()
                if extra_service_name:
                    extra_service = session.exec(
                        select(ExtraService).where(
                            ExtraService.name == extra_service_name
                        )
                    ).first()
                    extra_qty = (
                        int(row["extra_quantity"])
                        if row.get("extra_quantity", "").strip()
                        else 1
                    )
                    price_snapshot = (
                        extra_charge
                        if row.get("extra_charge", "").strip()
                        else extra_service.price
                    )
                    session.add(
                        JobItemExtra(
                            job_item_id=item.id,
                            extra_service_id=extra_service.id,
                            price_snapshot=price_snapshot,
                            name_snapshot=extra_service.name,
                            quantity=extra_qty,
                        )
                    )

        session.commit()

    if skipped:
        print(f"\n[WARN] {len(skipped)} problematic job items:")
        for s in skipped:
            print(f"  - {s}")


def seed_complete_job_order_info():
    unlogged_labels = seed_job_orders_from_csv()
    seed_job_items_from_csv(unlogged_labels=unlogged_labels)
