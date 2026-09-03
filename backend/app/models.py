import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, ForeignKey, Numeric
from sqlmodel import JSON, Field, Relationship, SQLModel

from app.enums import (
    AccountType,
    ExpenseCategory,
    JobStatus,
    PaymentStatus,
    PriceUnit,
    PricingStrategy,
    ReasonCategory,
    ReviewEntityType,
    SizeUnit,
    TransactionSource,
    UserRoles,
)


# ====================== AUDIT LOGS =========================
# For storing changes made by users on the database
class AuditLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    action: str
    user_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    user: User = Relationship(back_populates="audit_logs")

    @property
    def user_name(self) -> str | None:
        if self.user is None:
            return None
        return f"{self.user.first_name} {self.user.last_name}"


# ====================== USERS =========================
class UserBase(SQLModel):
    first_name: str = Field()
    last_name: str = Field()
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    role: UserRoles
    is_superAdmin: bool = Field(default=False)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    audit_logs: list[AuditLog] = Relationship(back_populates="user")
    voided_job_orders: list[JobOrder] = Relationship(
        back_populates="voided_by",
        sa_relationship_kwargs={
            "foreign_keys": "[JobOrder.voided_by_id]"
        },
    )
    created_for_reviews: list[ForReview] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={"foreign_keys": "[ForReview.created_by_id]"},
    )
    hashed_password: str = Field()


# ====================== CUSTOMERS =========================
# Customer info, customer is optional
class CustomerBase(SQLModel):
    name: str = Field(unique=True, index=True)
    address: str | None = None
    contact_no: str | None = None
    email: str | None = None


class Customer(CustomerBase, table=True):
    __tablename__ = "customers"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_orders: list[JobOrder] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ====================== SERVICE OPTIONS =========================
# Defines the options available for the services.
class ServiceOption(SQLModel, table=True):
    __tablename__ = "service_options"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    service_id: uuid.UUID = Field(foreign_key="services.id")

    name: str
    base_rate: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    is_active: bool = Field(default=True)
    minimum_consumption: float | None = Field(default=None)
    # For AREA services whose stock only comes in whole-unit increments along
    # one axis (e.g. tarpaulin rolls: only whole feet available, no 2.5ft).
    stock_increment: float | None = Field(default=None)

    service: Service = Relationship(back_populates="options")
    price_tiers: list[ServicePriceTier] = Relationship(
        back_populates="service_option",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    job_items: list[JobItem] = Relationship(back_populates="service_option")

    @property
    def full_service_name(self) -> str:
        if self.service and self.name != self.service.name:
            return f"{self.service.name} - {self.name}"
        return self.name

    @property
    def is_priced(self) -> bool:
        return self.base_rate is not None


# ====================== SERVICE TYPES =========================
# Defines the group of services
class ServiceBase(SQLModel):
    name: str = Field(unique=True, index=True)
    abbreviation: str = Field(unique=True, index=True)
    pricing_strategy: PricingStrategy
    unit: PriceUnit
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Service(ServiceBase, table=True):
    __tablename__ = "services"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_items: list[JobItem] = Relationship(back_populates="service")
    options: list[ServiceOption] = Relationship(
        back_populates="service",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ====================== SERVICE PRICE TIER =========================
# For services that have different tiers of pricing based on consumption.
# min_threshold defines the minimum consumption to reach a tier
# max_threshold defines the highest consumption before the next tier
class ServicePriceTier(SQLModel, table=True):
    __tablename__ = "service_price_tiers"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    service_option_id: uuid.UUID = Field(foreign_key="service_options.id")

    min_threshold: float
    max_threshold: float | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    rate: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))

    service_option: ServiceOption = Relationship(back_populates="price_tiers")


# ====================== EXTRA SERVICES =========================
# Holds all information about extra services similar to Service
class ExtraService(SQLModel, table=True):
    __tablename__ = "extra_services"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    price: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    job_item_extras: list[JobItemExtra] = Relationship(back_populates="extra_service")


# ====================== JOB ORDERS =========================
class JobOrderBase(SQLModel):
    jo_number: int = Field(unique=True, index=True)
    date_received: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    override_payment_status: PaymentStatus | None = Field(default=None)
    
    voided_at: datetime | None = Field(default=None)
    void_reason: str | None = Field(default=None)
    
    payment_status: PaymentStatus = Field(default=PaymentStatus.UNPAID, index=True)
    overall_job_status: JobStatus = Field(default=JobStatus.FOR_LAYOUT, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

class JobOrder(JobOrderBase, table=True):
    __tablename__ = "job_orders"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=True)
    )
    created_by_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )
    updated_by_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )

    created_by: User = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[JobOrder.created_by_id]"}
    )
    updated_by: User = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[JobOrder.updated_by_id]"}
    )
    voided_by_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    voided_by: User | None = Relationship(
        back_populates="voided_job_orders",
        sa_relationship_kwargs={
            "foreign_keys": "[JobOrder.voided_by_id]"
        },
    )
    customer: Customer | None = Relationship(back_populates="job_orders")
    job_items: list[JobItem] = Relationship(
        back_populates="job_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    payments: list[Payment] = Relationship(
        back_populates="job_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    claiming_history: list[ClaimingHistory] = Relationship(
        back_populates="job_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    
    @property
    def is_void(self) -> bool:
        return self.voided_at is not None

    @property
    def total_due(self) -> Decimal:
        return sum((item.subtotal for item in self.job_items), Decimal(0))

    @property
    def total_paid(self) -> Decimal:
        return sum((p.amount for p in self.payments), Decimal(0))

    @property
    def balance(self) -> Decimal:
        return self.total_due - self.total_paid

    @property
    def computed_payment_status(self) -> PaymentStatus:
        if self.override_payment_status:
            return self.override_payment_status
        if self.total_paid <= 0:
            return PaymentStatus.UNPAID
        elif self.total_paid == self.total_due:
            return PaymentStatus.FULLY_PAID
        elif self.total_paid > self.total_due:
            return PaymentStatus.OVERCHARGED
        else:
            return PaymentStatus.PARTIAL

    @property
    def computed_overall_job_status(self) -> JobStatus:
        if not self.job_items:
            return JobStatus.PENDING

        priorities = {
            JobStatus.CANCELLED: 0,
            JobStatus.PENDING: 1,
            JobStatus.RELEASED: 2,
            JobStatus.FOR_PICKUP: 3,
            JobStatus.FOR_PRINTING: 4,
            JobStatus.FOR_APPROVAL: 5,
            JobStatus.FOR_LAYOUT: 6,
        }
        return max(
            self.job_items, key=lambda item: priorities.get(item.job_status, -1)
        ).job_status

    def sync_computed_fields(self):
        self.payment_status = self.computed_payment_status
        self.overall_job_status = self.computed_overall_job_status

    @property
    def customer_name(self) -> str | None:
        return self.customer.name if self.customer else None

    @property
    def customer_email(self) -> str | None:
        return self.customer.email if self.customer else None

    @property
    def customer_contact_no(self) -> str | None:
        return self.customer.contact_no if self.customer else None

    @property
    def created_by_name(self) -> str | None:
        return (
            f"{self.created_by.first_name} {self.created_by.last_name}"
            if self.created_by
            else None
        )

    @property
    def updated_by_name(self) -> str | None:
        return (
            f"{self.updated_by.first_name} {self.updated_by.last_name}"
            if self.updated_by
            else None
        )

    @property
    def voided_by_name(self) -> str | None:
        return (
            f"{self.updated_by.first_name} {self.updated_by.last_name}"
            if self.updated_by
            else None
        )


# ====================== JOB ITEM EXTRAS =========================
class JobItemExtra(SQLModel, table=True):
    __tablename__ = "job_item_extras"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_item_id: uuid.UUID = Field(foreign_key="job_items.id")

    extra_service_id: uuid.UUID = Field(foreign_key="extra_services.id")

    quantity: int
    price_snapshot: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    name_snapshot: str

    job_item: JobItem = Relationship(back_populates="extras")

    extra_service: ExtraService = Relationship(back_populates="job_item_extras")


# ====================== JOB ITEMS =========================
class JobItemBase(SQLModel):
    item_id: str = Field(unique=True, index=True)

    description: str | None = Field(default=None)

    # Things affecting pricing
    height: float | None = Field(default=None)
    width: float | None = Field(default=None)
    size_unit: SizeUnit | None = Field(default=None)
    quantity: int = Field(default=1)

    # Workflow related
    job_status: JobStatus
    due_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    notes: str | None = Field(default=None)

    # Pricing data
    # extra_charge is used for rounding up, discount can also be used to round down
    discount_amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    extra_charge: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))


class JobItem(JobItemBase, table=True):
    __tablename__ = "job_items"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_order_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_orders.id", ondelete="CASCADE"), nullable=False
        )
    )
    service_id: uuid.UUID = Field(foreign_key="services.id")
    service_option_id: uuid.UUID = Field(foreign_key="service_options.id")
    job_order: JobOrder = Relationship(back_populates="job_items")
    service: Service = Relationship(back_populates="job_items")
    service_option: ServiceOption = Relationship(back_populates="job_items")
    claiming_history: list[ClaimingHistory] = Relationship(back_populates="job_item")
    extras: list[JobItemExtra] = Relationship(
        back_populates="job_item",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    unit_price: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    subtotal: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    service_name_snapshot: str
    service_option_name_snapshot: str
    service_abbreviation_snapshot: str

    @property
    def total_claimed(self) -> int:
        return sum(c.pcs_claimed for c in self.claiming_history)

    @property
    def remaining_on_hand(self) -> int:
        return self.quantity - self.total_claimed

    @property
    def is_fully_claimed(self):
        return self.remaining_on_hand == 0


# ====================== PAYMENTS =========================
class PaymentBase(SQLModel):
    date_received: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    reference_number: str | None = Field(default=None)
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    notes: str | None = Field(default=None)


class Payment(PaymentBase, table=True):
    __tablename__ = "payments"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_name_snapshot: str
    job_order_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_orders.id", ondelete="CASCADE"), nullable=False
        )
    )
    account: Account = Relationship(back_populates="payments")
    account_id: uuid.UUID = Field(foreign_key="accounts.id", nullable=False)

    job_order: JobOrder = Relationship(back_populates="payments")
    
    
# ====================== REFUNDS =========================
class RefundBase(SQLModel):
    date_issued: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    reason: str = Field()
        
    
class Refund(RefundBase, table=True):
    __tablename__ = "refunds"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_name_snapshot: str
    
    account_id: uuid.UUID = Field(foreign_key="accounts.id", nullable=False)
    payment_id: uuid.UUID = Field(foreign_key="")
    
    account: Account = Relationship(back_populates="payments")


# ====================== CLAIMING HISTORY =========================
class ClaimingHistoryBase(SQLModel):
    date_claimed: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    name: str = Field()
    pcs_claimed: int = Field(default=0)
    claimed_item_id: str = Field()


class ClaimingHistory(ClaimingHistoryBase, table=True):
    __tablename__ = "claiming_history"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_order_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_orders.id", ondelete="CASCADE"), nullable=False
        )
    )
    job_item_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("job_items.id", ondelete="CASCADE"), nullable=False)
    )

    job_order: JobOrder = Relationship(back_populates="claiming_history")
    job_item: JobItem = Relationship(back_populates="claiming_history")


# ====================== EXPENSES =========================
class ExpenseBase(SQLModel):
    date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    category: ExpenseCategory
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    description: str = Field()
    is_archived: bool = Field(default=False)


class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="accounts.id", nullable=False)
    account_name_snapshot: str

    account: Account = Relationship(back_populates="expenses")

    @property
    def account_name(self) -> str:
        return self.account.name


# ====================== MISC SALES =========================
class MiscSaleBase(SQLModel):
    date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    description: str = Field()
    reference_number: str | None = Field(default=None, nullable=True)
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    is_archived: bool = Field(default=False)


class MiscSale(MiscSaleBase, table=True):
    __tablename__ = "misc_sales"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="accounts.id", nullable=False, index=True)
    account_name_snapshot: str
    
    account: Account = Relationship(back_populates="misc_sales")
    
    @property
    def account_name(self) -> str | None:
        return self.account.name if self.account else None


# ====================== ACCOUNTS =========================
class Account(SQLModel, table=True):
    __tablename__ = "accounts"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)  # "Cash on Hand", "BPI Savings", "GCash"
    type: AccountType = Field()
    beginning_balance: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    beginning_balance_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = Field(default=True)

    payments: list[Payment] = Relationship(back_populates="account")
    unlinked_payments: list[UnlinkedPayment] = Relationship(back_populates="account")
    transactions: list[AccountTransaction] = Relationship(back_populates="account")
    expenses: list[Expense] = Relationship(back_populates="account")
    misc_sales: list[MiscSale] = Relationship(back_populates="account")

    @property
    def current_balance(self) -> Decimal:
        return self.beginning_balance + sum(
            (transaction.amount for transaction in self.transactions),
            Decimal("0.00"),
        )


class AccountTransaction(SQLModel, table=True):
    __tablename__ = "account_transactions"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="accounts.id", index=True)
    date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    amount: Decimal = Field(
        sa_column=Column(Numeric(12, 2), nullable=False)
    )  # positive = in, negative = out
    source_type: TransactionSource
    source_id: uuid.UUID | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    account: Account = Relationship(back_populates="transactions")


# ====================== UNLINKED PAYMENTS =========================
# Temporary table. No payments should be unlinked. It should either be linked to a job order or a misc sale.
# For payments known to be for a real job order, but where that job order
# can't be identified from past records.
class UnlinkedPayment(SQLModel, table=True):
    __tablename__ = "unlinked_payments"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_received: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    reference_number: str | None = Field(default=None)
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    customer_name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    account_id: uuid.UUID = Field(foreign_key="accounts.id", nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    account: Account = Relationship(back_populates="unlinked_payments")

    @property
    def account_name(self) -> str | None:
        return self.account.name if self.account else None


# ====================== FOR REVIEW =========================
# For any records that have missing or inconsistent data, so they can be reviewed by a human.
# It would use their tables and just link here by ID so that the human can see the record in its original table and fix it, then remove it from this table.
class ForReview(SQLModel, table=True):
    __tablename__ = "for_reviews"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    entity_type: ReviewEntityType
    entity_id: uuid.UUID = Field()
    entity_reference: str = Field()
    reason_category: ReasonCategory
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))
    reason: str = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by_id: uuid.UUID = Field(foreign_key="users.id")

    created_by: User = Relationship(
        back_populates="created_for_reviews",
        sa_relationship_kwargs={"foreign_keys": "[ForReview.created_by_id]"},
    )

    @property
    def created_by_name(self) -> str:
        return self.created_by.username