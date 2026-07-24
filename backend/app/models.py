from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey
from datetime import datetime, timezone
import uuid
from pydantic import EmailStr
from app.enums import (
    UserRoles,
    SizeUnit,
    PaymentStatus,
    JobStatus,
    ExpenseCategory,
    AccountType,
    TransactionSource,
    PricingStrategy,
    PriceUnit,
    ReviewEntityType,
    ReasonCategory
)


# ====================== AUDIT LOGS =========================
# For storing changes made by users on the database
class AuditLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    action: str
    user_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="audit_logs")

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
    audit_logs: list["AuditLog"] = Relationship(back_populates="user")
    void_job_orders: list["VoidJobOrder"] = Relationship(back_populates="voided_by")
    created_for_reviews: list["ForReview"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={"foreign_keys": "[ForReview.created_by_id]"}
    )
    resolved_for_reviews: list["ForReview"] = Relationship(
        back_populates="resolved_by",
        sa_relationship_kwargs={"foreign_keys": "[ForReview.resolved_by_id]"}
    )
    hashed_password: str = Field()


# ====================== CUSTOMERS =========================
# Customer info, only name is required but users still should try to fill at least contact_number or email
class CustomerBase(SQLModel):
    name: str = Field(unique=True, index=True)
    address: str | None = None
    contact_no: str | None = None
    email: str | None = None


class Customer(CustomerBase, table=True):
    __tablename__ = "customers"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_orders: list["JobOrder"] = Relationship(
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
    base_rate: float
    is_active: bool = Field(default=True)
    minimum_consumption: float | None = Field(default=None)
    # For AREA services whose stock only comes in whole-unit increments along
    # one axis (e.g. tarpaulin rolls: only whole feet available, no 2.5ft).
    stock_increment: float | None = Field(default=None)

    service: "Service" = Relationship(back_populates="options")
    price_tiers: list["ServicePriceTier"] = Relationship(
        back_populates="service_option",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    job_items: list["JobItem"] = Relationship(back_populates="service_option")

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Service(ServiceBase, table=True):
    __tablename__ = "services"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_items: list["JobItem"] = Relationship(back_populates="service")
    options: list["ServiceOption"] = Relationship(
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

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    rate: float = Field(default=0.0)

    service_option: "ServiceOption" = Relationship(back_populates="price_tiers")


# ====================== EXTRA SERVICES =========================
# Holds all information about extra services similar to Service
class ExtraService(SQLModel, table=True):
    __tablename__ = "extra_services"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    price: float = Field(default=0.0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    job_item_extras: list["JobItemExtra"] = Relationship(back_populates="extra_service")


# ====================== JOB ORDERS =========================
class JobOrderBase(SQLModel):
    jo_number: int = Field(unique=True, index=True)
    date_received: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    override_payment_status: PaymentStatus | None = Field(default=None)
    is_active: bool = Field(default=True)
    payment_status: PaymentStatus = Field(default=PaymentStatus.UNPAID, index=True)
    overall_job_status: JobStatus = Field(default=JobStatus.FOR_LAYOUT, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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

    created_by: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[JobOrder.created_by_id]"}
    )
    updated_by: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[JobOrder.updated_by_id]"}
    )
    customer: "Customer" = Relationship(back_populates="job_orders")
    job_items: list["JobItem"] = Relationship(
        back_populates="job_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    payments: list["Payment"] = Relationship(
        back_populates="job_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    claims: list["ClaimingHistory"] = Relationship(
        back_populates="job_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    @property
    def total_due(self) -> float:
        return sum(item.subtotal for item in self.job_items)

    @property
    def total_paid(self) -> float:
        return sum(p.amount for p in self.payments)

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
            return JobStatus.CANCELLED

        priorities = {
            JobStatus.CANCELLED: 0,
            JobStatus.RELEASED: 1,
            JobStatus.FOR_PICKUP: 2,
            JobStatus.FOR_PRINTING: 3,
            JobStatus.FOR_APPROVAL: 4,
            JobStatus.FOR_LAYOUT: 5,
        }
        return max(
            self.job_items, key=lambda item: priorities.get(item.job_status, -1)
        ).job_status

    def sync_computed_fields(self):
        self.payment_status = self.computed_payment_status
        self.overall_job_status = self.computed_overall_job_status

    @property
    def customer_name(self) -> str | None:
        return self.customer.name

    @property
    def customer_email(self) -> str | None:
        return self.customer.email

    @property
    def customer_contact_no(self) -> str | None:
        return self.customer.contact_no

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


# ====================== JOB ITEM EXTRAS =========================
class JobItemExtra(SQLModel, table=True):
    __tablename__ = "job_item_extras"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_item_id: uuid.UUID = Field(foreign_key="job_items.id")

    extra_service_id: uuid.UUID = Field(foreign_key="extra_services.id")

    quantity: int
    price_snapshot: float
    name_snapshot: str

    job_item: "JobItem" = Relationship(back_populates="extras")

    extra_service: "ExtraService" = Relationship(back_populates="job_item_extras")


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
    due_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str | None = Field(default=None)

    # Pricing data
    # extra_charge is used for rounding up, discount can also be used to round down
    unit_price: float = Field(default=0.0)
    discount_amount: float = Field(default=0.0)
    extra_charge: float = Field(default=0.0)
    subtotal: float = Field(default=0.0)

    service_name_snapshot: str
    service_option_name_snapshot: str
    service_abbreviation_snapshot: str


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
    job_order: "JobOrder" = Relationship(back_populates="job_items")
    service: "Service" = Relationship(back_populates="job_items")
    service_option: "ServiceOption" = Relationship(back_populates="job_items")
    claims: list["ClaimingHistory"] = Relationship(back_populates="job_item")
    extras: list["JobItemExtra"] = Relationship(
        back_populates="job_item",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    @property
    def total_claimed(self) -> int:
        return sum(c.pcs_claimed for c in self.claims)

    @property
    def remaining_on_hand(self) -> int:
        return self.quantity - self.total_claimed

    @property
    def service_name(self):
        return self.service_name_snapshot

    @property
    def is_fully_claimed(self):
        return self.remaining_on_hand == 0


# ====================== PAYMENTS =========================
class PaymentBase(SQLModel):
    date_received: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reference_number: str | None = Field(default=None)
    amount: float = Field(default=0.0)
    notes: str | None = Field(default=None)


class Payment(PaymentBase, table=True):
    __tablename__ = "payments"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_order_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_orders.id", ondelete="CASCADE"), nullable=False
        )
    )
    account: "Account" = Relationship(back_populates="payments")
    account_id: uuid.UUID = Field(foreign_key="accounts.id", nullable=False)

    job_order: "JobOrder" = Relationship(back_populates="payments")

    @property
    def account_name(self) -> str:
        return self.account.name


# ====================== CLAIMING HISTORY =========================
class ClaimingHistoryBase(SQLModel):
    date_claimed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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

    job_order: "JobOrder" = Relationship(back_populates="claims")
    job_item: "JobItem" = Relationship(back_populates="claims")


# ====================== EXPENSES =========================
class ExpenseBase(SQLModel):
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    category: ExpenseCategory
    amount: float = Field()
    description: str = Field()
    is_archived: bool = Field(default=False)


class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="accounts.id", nullable=False)

    account: "Account" = Relationship(back_populates="expenses")

    @property
    def account_name(self) -> str:
        return self.account.name


# ====================== MISC SALES =========================
class MiscSaleBase(SQLModel):
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = Field()
    amount: float = Field()
    is_archived: bool = Field(default=False)


class MiscSale(MiscSaleBase, table=True):
    __tablename__ = "misc_sales"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# ====================== ACCOUNTS =========================
class Account(SQLModel, table=True):
    __tablename__ = "accounts"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)  # "Cash on Hand", "BPI Savings", "GCash"
    type: AccountType = Field()
    beginning_balance: float = Field(default=0.0)
    beginning_balance_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    current_balance: float = Field(default=0.0)
    is_active: bool = Field(default=True)

    payments: list["Payment"] = Relationship(back_populates="account")
    unlinked_payments: list["UnlinkedPayment"] = Relationship(back_populates="account")
    transactions: list["AccountTransaction"] = Relationship(back_populates="account")
    expenses: list["Expense"] = Relationship(back_populates="account")


class AccountTransaction(SQLModel, table=True):
    __tablename__ = "account_transactions"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="accounts.id")
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = Field()
    amount: float = Field()  # positive = in, negative = out
    running_balance: float = Field()
    source_type: TransactionSource
    source_id: uuid.UUID | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    account: "Account" = Relationship(back_populates="transactions")


# ====================== VOID JOB ORDERS =========================
# For Jobs that are either cancelled or the physical paper is missing
# This table exists purely so the users can verify every JO number is accounted for
class VoidJobOrder(SQLModel, table=True):
    __tablename__ = "void_job_orders"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    jo_number: int = Field(unique=True, index=True)
    job_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    voided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str
    created_by_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)

    voided_by: "User" = Relationship(back_populates="void_job_orders")

    @property
    def voided_by_name(self) -> str:
        return self.voided_by.username if self.voided_by else "N/A"

# ====================== UNLINKED PAYMENTS =========================
# For payments known to be for a real job order, but where that job order
# can't be identified from past records.
class UnlinkedPayment(SQLModel, table=True):
    __tablename__ = "unlinked_payments"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_received: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reference_number: str | None = Field(default=None)
    amount: float = Field(default=0.0)
    customer_name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    account_id: uuid.UUID = Field(foreign_key="accounts.id", nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    account: "Account" = Relationship(back_populates="unlinked_payments")


# ====================== FOR REVIEW =========================
# For any records that have missing or inconsistent data, so they can be reviewed by a human.
# It would use their tables and just link here by ID so that the human can see the record in its original table and fix it, then remove it from this table.
class ForReview(SQLModel, table=True):
    __tablename__ = "for_review"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    entity_type: ReviewEntityType
    entity_id: uuid.UUID = Field()
    entity_reference: str = Field()
    reason_category: ReasonCategory
    reason: str = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by_id: uuid.UUID | None = Field(foreign_key="users.id")
    resolved_at: datetime | None = Field(default=None)
    resolved_by_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")

    created_by: "User" = Relationship(
        back_populates="created_for_reviews",
        sa_relationship_kwargs={"foreign_keys": "[ForReview.created_by_id]"}
    )
    resolved_by: "User" = Relationship(
        back_populates="resolved_for_reviews",
        sa_relationship_kwargs={"foreign_keys": "[ForReview.resolved_by_id]"}
    )

    @property
    def created_by_name(self) -> str:
        return self.created_by.username

    @property
    def resolved_by_name(self) -> str | None:
        return self.resolved_by.username if self.resolved_by else None