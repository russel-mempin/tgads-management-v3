from collections import defaultdict
from datetime import UTC, date, datetime, time
from decimal import ROUND_CEILING, Decimal

from sqlalchemy import case, func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.enums import SizeUnit, TransactionSource
from app.models import (
    Account,
    AccountTransaction,
    Expense,
    JobItem,
    JobOrder,
    MiscSale,
    Payment,
    ServiceOption,
)
from app.schemas.performance import (
    CustomerPerformance,
    JobOrderSales,
    MonthlyPerformance,
    MonthlyPerformanceBase,
    PerAccountCollections,
    ServicePerformance,
)


# TODO: Fully AI generated
def to_feet(value: float, unit: SizeUnit) -> Decimal:
    value = Decimal(str(value))

    conversions = {
        SizeUnit.METER: Decimal("3.280839895"),
        SizeUnit.INCHES: Decimal(1) / Decimal(12),
        SizeUnit.FEET: Decimal(1),
        SizeUnit.CENTIMETER: Decimal(1) / Decimal("30.48"),
        SizeUnit.MILLIMETER: Decimal(1) / Decimal("304.8"),
    }

    return value * conversions[unit]


# TODO: Fully AI generated
def calculate_material_consumption(item: JobItem) -> Decimal:
    if item.height is None or item.width is None or item.size_unit is None:
        return Decimal(0)

    height = to_feet(item.height, item.size_unit)
    width = to_feet(item.width, item.size_unit)

    # Some materials require whole-foot width increments.
    if item.service_option.use_whole_foot_width:
        width = width.to_integral_value(rounding=ROUND_CEILING)

    return height * width * item.quantity


# TODO: Fully AI generated
def get_service_performances(
    db: Session,
    month_start: date,
    next_month: date,
) -> list[ServicePerformance]:

    job_items = db.exec(
        select(JobItem)
        .join(JobOrder)
        .where(
            JobOrder.date_received >= month_start,
            JobOrder.date_received < next_month,
            JobOrder.voided_at.is_(None),
        )
        .options(
            selectinload(JobItem.service_option).selectinload(ServiceOption.service)
        )
    ).all()

    service_data = defaultdict(
        lambda: {
            "full_service_name": "",
            "order_quantity": 0,
            "material_consumed_in_sqft": Decimal(0),
            "sales": Decimal(0),
        }
    )

    for item in job_items:
        option_id = item.service_option_id

        data = service_data[option_id]

        data["full_service_name"] = item.service_option.full_service_name

        data["order_quantity"] += item.quantity

        data["material_consumed_in_sqft"] += calculate_material_consumption(item)

        data["sales"] += item.subtotal

    total_sales = sum(
        (data["sales"] for data in service_data.values()),
        Decimal(0),
    )

    performances = []

    for data in service_data.values():
        sales_percentage = (
            float(data["sales"] / total_sales * 100) if total_sales > 0 else 0.0
        )

        performances.append(
            ServicePerformance(
                full_service_name=data["full_service_name"],
                order_quantity=data["order_quantity"],
                material_consumed_in_sqft=data["material_consumed_in_sqft"],
                sales=data["sales"],
                sales_percentage=sales_percentage,
            )
        )

    performances.sort(
        key=lambda x: x.sales,
        reverse=True,
    )

    return performances


# TODO: Fully AI generated
def get_customer_performances(
    db: Session,
    month_start: date,
    next_month: date,
    limit: int = 10,
) -> list[CustomerPerformance]:

    job_orders = db.exec(
        select(JobOrder)
        .where(
            JobOrder.date_received >= month_start,
            JobOrder.date_received < next_month,
            JobOrder.voided_at.is_(None),
        )
        .options(
            selectinload(JobOrder.customer),
            selectinload(JobOrder.job_items),
            selectinload(JobOrder.payments),
        )
    ).all()

    customer_data = defaultdict(
        lambda: {
            "name": "",
            "order_quantity": 0,
            "sales": Decimal(0),
            "balance": Decimal(0),
            "last_order": None,
        }
    )

    for job_order in job_orders:
        customer_id = job_order.customer_id

        data = customer_data[customer_id]

        # Customer information
        data["name"] = job_order.customer_name

        # Number of job orders
        data["order_quantity"] += 1

        # Total sales for this job order
        total_due = sum(
            (item.subtotal for item in job_order.job_items),
            Decimal(0),
        )

        data["sales"] += total_due

        next_month_datetime = datetime.combine(
            next_month,
            time.min,
            tzinfo=UTC,
        )

        # Payments received before the next month
        total_paid = sum(
            (
                payment.amount
                for payment in job_order.payments
                if payment.date_received < next_month_datetime
            ),
            Decimal(0),
        )

        # Outstanding balance as of month-end
        data["balance"] += total_due - total_paid

        # Most recent order
        if data["last_order"] is None or job_order.date_received > data["last_order"]:
            data["last_order"] = job_order.date_received

    # Calculate total sales across all customers
    total_sales = sum(
        (data["sales"] for data in customer_data.values()),
        Decimal(0),
    )

    performances = []

    for data in customer_data.values():
        sales_percentage = (
            float(data["sales"] / total_sales * 100) if total_sales > 0 else 0.0
        )

        performances.append(
            CustomerPerformance(
                name=data["name"],
                order_quantity=data["order_quantity"],
                sales=data["sales"],
                balance=data["balance"],
                last_order=data["last_order"],
                sales_percentage=sales_percentage,
            )
        )

    # Highest sales first
    performances.sort(
        key=lambda x: x.sales,
        reverse=True,
    )

    return performances[:limit]


# TODO: Fully AI generated
def get_monthly_performance_list(
    db: Session, year: int
) -> list[MonthlyPerformanceBase]:
    collected = func.coalesce(
        func.sum(
            case(
                (
                    AccountTransaction.source_type.in_(
                        [
                            TransactionSource.PAYMENT,
                            TransactionSource.BANK_INTEREST,
                            TransactionSource.MISC_SALE,
                        ]
                    ),
                    AccountTransaction.amount,
                ),
                (
                    AccountTransaction.source_type == TransactionSource.REVERSAL,
                    case(
                        (AccountTransaction.amount < 0, AccountTransaction.amount),
                        else_=0,
                    ),
                ),
                else_=0,
            )
        ),
        0,
    )

    expenses = func.coalesce(
        func.sum(
            case(
                (
                    AccountTransaction.source_type.in_(
                        [
                            TransactionSource.EXPENSE,
                            TransactionSource.REFUND,
                        ]
                    ),
                    func.abs(AccountTransaction.amount),
                ),
                (
                    AccountTransaction.source_type == TransactionSource.REVERSAL,
                    case(
                        (AccountTransaction.amount > 0, -AccountTransaction.amount),
                        else_=0,
                    ),
                ),
                else_=0,
            )
        ),
        0,
    )

    statement = (
        select(
            func.extract("month", AccountTransaction.date).label("month"),
            collected.label("collected"),
            expenses.label("expenses"),
        )
        .where(
            AccountTransaction.date >= date(year, 1, 1),
            AccountTransaction.date < date(year + 1, 1, 1),
        )
        .group_by(func.extract("month", AccountTransaction.date))
        .order_by(func.extract("month", AccountTransaction.date))
    )

    results = db.exec(statement).all()

    monthly_data = {int(row.month): row for row in results}

    performance = []

    for month in range(1, 13):
        month_start = date(year, month, 1)

        next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

        # Total value of job orders received this month
        job_totals = (
            select(
                JobItem.job_order_id,
                func.sum(JobItem.subtotal).label("total_due"),
            )
            .group_by(JobItem.job_order_id)
            .subquery()
        )

        # Payments received up to the end of this month
        payment_totals = (
            select(
                Payment.job_order_id,
                func.sum(Payment.amount).label("total_paid"),
            )
            .where(Payment.date_received < next_month)
            .group_by(Payment.job_order_id)
            .subquery()
        )

        job_performance = (
            select(
                func.coalesce(func.sum(job_totals.c.total_due), 0).label("sales"),
                func.coalesce(
                    func.sum(
                        job_totals.c.total_due
                        - func.coalesce(payment_totals.c.total_paid, 0)
                    ),
                    0,
                ).label("receivables"),
            )
            .select_from(JobOrder)
            .outerjoin(
                job_totals,
                job_totals.c.job_order_id == JobOrder.id,
            )
            .outerjoin(
                payment_totals,
                payment_totals.c.job_order_id == JobOrder.id,
            )
            .where(
                JobOrder.date_received >= month_start,
                JobOrder.date_received < next_month,
            )
        )

        job_result = db.exec(job_performance).one()

        transaction = monthly_data.get(month)

        collected_amount = transaction.collected if transaction else Decimal("0.00")
        expenses_amount = transaction.expenses if transaction else Decimal("0.00")

        performance.append(
            MonthlyPerformanceBase(
                month=month,
                collected=collected_amount,
                expenses=expenses_amount,
                net=collected_amount - expenses_amount,
                sales=job_result.sales,
                receivables=job_result.receivables,
            )
        )

    return performance


def _get_account_snapshots(
    db: Session, month_start: datetime, next_month: datetime
) -> list[PerAccountCollections]:
    # Get all accounts
    # Get all transactions of the month
    # Somehow filter collections and collections
    # Return all data per account
    # Also include transfers data
    accounts = db.exec(select(Account)).all()

    transactions = db.exec(
        select(AccountTransaction).where(
            AccountTransaction.date >= month_start, AccountTransaction.date < next_month
        )
    ).all()

    account_data = defaultdict(
        lambda: {
            "collections": Decimal("0.00"),
            "deductions": Decimal("0.00"),
            "ending_balance": Decimal("0.00"),
        }
    )

    # For every account, initialize the dict's ending balance to prepare it for collections and deductions.
    for account in accounts:
        account_data[account.id]["ending_balance"] = account.beginning_balance

    accounts_by_id = {account.id: account for account in accounts}
    for transaction in transactions:
        # Get the account id in the transaction and match it with the accounts_by_id
        account = accounts_by_id.get(transaction.account_id)
        # Skip conditions
        if account is None:
            continue

        if transaction.date < account.beginning_balance_date:
            continue
        
        # Collections
        if transaction.source_type in (
            TransactionSource.PAYMENT,
            TransactionSource.BANK_INTEREST,
            TransactionSource.MISC_SALE,
        ):
            data = account_data[account.id]
            data["collections"] += transaction.amount

        # Deductions
        if transaction.source_type in (
            TransactionSource.EXPENSE,
            TransactionSource.REFUND,
        ):
            data = account_data[account.id]
            data["deductions"] += abs(transaction.amount)

    return [
        PerAccountCollections(
            account_name=account.name,
            collections=account_data[account.id]["collections"],
            deductions=account_data[account.id]["deductions"],
            transfer_in=0,
            transfer_out=0,
            ending_balance=account_data[account.id]["ending_balance"]
            + account_data[account.id]["collections"]
            - account_data[account.id]["deductions"],
        )
        for account in accounts
    ]


# TODO: Fully AI generated
def get_monthly_performance(
    db: Session,
    year: int,
    month: int,
) -> MonthlyPerformance:
    month_start = date(year, month, 1)

    next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    # Collected transactions
    # TODO: Tama output pero pwede pa rewrite para mas maintindihan ko
    collected = func.coalesce(
        func.sum(
            case(
                (
                    AccountTransaction.source_type.in_(
                        [
                            TransactionSource.PAYMENT,
                            TransactionSource.BANK_INTEREST,
                            TransactionSource.MISC_SALE,
                        ]
                    ),
                    AccountTransaction.amount,
                ),
                (
                    AccountTransaction.source_type == TransactionSource.REVERSAL,
                    case(
                        (AccountTransaction.amount < 0, AccountTransaction.amount),
                        else_=0,
                    ),
                ),
                else_=0,
            )
        ),
        0,
    )
    # TODO: Tama output pero pwede pa rewrite para mas maintindihan ko
    collected_list = db.exec(
        select(AccountTransaction).where(
            AccountTransaction.source_type.in_(
                [
                    TransactionSource.PAYMENT,
                    TransactionSource.BANK_INTEREST,
                    TransactionSource.MISC_SALE,
                ]
            )
            | (
                (AccountTransaction.source_type == TransactionSource.REVERSAL)
                & (AccountTransaction.amount < 0)
            )
        )
    ).all()

    # Expense transactions
    expenses = func.coalesce(
        func.sum(
            case(
                (
                    AccountTransaction.source_type.in_(
                        [
                            TransactionSource.EXPENSE,
                            TransactionSource.REFUND,
                        ]
                    ),
                    func.abs(AccountTransaction.amount),
                ),
                (
                    AccountTransaction.source_type == TransactionSource.REVERSAL,
                    case(
                        (AccountTransaction.amount > 0, -AccountTransaction.amount),
                        else_=0,
                    ),
                ),
                else_=0,
            )
        ),
        0,
    )

    # Get collected and expenses for the requested month
    transaction_statement = select(
        collected.label("collected"),
        expenses.label("expenses"),
    ).where(
        AccountTransaction.date >= month_start,
        AccountTransaction.date < next_month,
    )

    transaction_result = db.exec(transaction_statement).one()

    # Total value of job items per job order
    job_totals = (
        select(
            JobItem.job_order_id,
            func.sum(JobItem.subtotal).label("total_due"),
        )
        .group_by(JobItem.job_order_id)
        .subquery()
    )

    # Payments received up to the end of the requested month
    payment_totals = (
        select(
            Payment.job_order_id,
            func.sum(Payment.amount).label("total_paid"),
        )
        .where(
            Payment.date_received < next_month,
        )
        .group_by(Payment.job_order_id)
        .subquery()
    )

    # Calculate sales and receivables
    job_performance = (
        select(
            func.coalesce(func.sum(job_totals.c.total_due), 0).label("sales"),
            func.coalesce(
                func.sum(
                    job_totals.c.total_due
                    - func.coalesce(payment_totals.c.total_paid, 0)
                ),
                0,
            ).label("receivables"),
        )
        .select_from(JobOrder)
        .outerjoin(
            job_totals,
            job_totals.c.job_order_id == JobOrder.id,
        )
        .outerjoin(
            payment_totals,
            payment_totals.c.job_order_id == JobOrder.id,
        )
        .where(
            JobOrder.date_received >= month_start,
            JobOrder.date_received < next_month,
            JobOrder.voided_at.is_(None),
        )
    )

    job_result = db.exec(job_performance).one()

    # Final calculations
    collected_amount = transaction_result.collected
    expenses_amount = transaction_result.expenses

    month_start = date(year, month, 1)

    next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    month_start_datetime = datetime.combine(
        month_start,
        time.min,
        tzinfo=UTC,
    )

    next_month_datetime = datetime.combine(
        next_month,
        time.min,
        tzinfo=UTC,
    )

    snapshots_of_accounts = _get_account_snapshots(
        db,
        month_start_datetime,
        next_month_datetime,
    )

    # Customer performance data
    customer_performances = get_customer_performances(
        db,
        month_start,
        next_month,
    )

    # Service performance data
    service_performances = get_service_performances(
        db,
        month_start,
        next_month,
    )

    # Job Order payment data
    job_orders = db.exec(
        select(JobOrder).where(
            JobOrder.date_received >= month_start,
            JobOrder.date_received < next_month,
            JobOrder.voided_at.is_(None),
        )
    ).all()

    job_order_sales = [
        JobOrderSales(
            jo_number=jo.jo_number,
            customer_name=jo.customer_name,
            date_received=jo.date_received,
            total_due=jo.total_due,
            total_paid=jo.total_paid,
            balance=jo.balance,
        )
        for jo in job_orders
    ]

    misc_sales_list = db.exec(
        select(MiscSale).where(
            MiscSale.date >= datetime(2026, 1, 1, tzinfo=UTC),
            MiscSale.date < datetime(2026, 2, 1, tzinfo=UTC),
        )
    ).all()

    expenses_list = db.exec(
        select(Expense).where(
            Expense.date >= datetime(2026, 1, 1, tzinfo=UTC),
            Expense.date < datetime(2026, 2, 1, tzinfo=UTC),
        )
    ).all()

    return MonthlyPerformance(
        month=month,
        collected=collected_amount,
        expenses=expenses_amount,
        net=collected_amount - expenses_amount,
        sales=job_result.sales,
        receivables=job_result.receivables,
        snapshots_of_accounts=snapshots_of_accounts,
        collected_list=collected_list,
        customer_performances=customer_performances,
        service_performances=service_performances,
        job_order_sales=job_order_sales,
        miscellaneous_sales_list=misc_sales_list,
        expenses_list=expenses_list,
    )
