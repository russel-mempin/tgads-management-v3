from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel

from app.schemas.expense import ExpensePublic
from app.schemas.misc_sale import MiscSalePublic


class CustomerPerformance(SQLModel):
    name: str | None
    order_quantity: int
    sales: Decimal
    balance: Decimal
    last_order: datetime
    sales_percentage: float


class ServicePerformance(SQLModel):
    full_service_name: str
    order_quantity: int
    material_consumed_in_sqft: Decimal
    sales: Decimal
    sales_percentage: float


class JobOrderSales(SQLModel):
    jo_number: int
    customer_name: str | None
    date_received: datetime
    total_due: Decimal
    total_paid: Decimal
    balance: Decimal


class PerAccountCollections(SQLModel):
    account_name: str
    collections: Decimal
    deductions: Decimal
    ending_balance: Decimal


class MonthlyPerformanceBase(SQLModel):
    month: int
    collected: Decimal # Sum of collections for the month. (Money on account)
    expenses: Decimal # Sum of expenses for the month
    net: Decimal # Collected - expenses
    sales: Decimal # Total sales regardless of payment status of the job order
    receivables: Decimal # Total of receivables until the end of the month


class MonthlyPerformance(MonthlyPerformanceBase):
    snapshots_of_accounts: list[PerAccountCollections]# Snapshots of all accounts at the end of the month
    customer_performances: list[CustomerPerformance] # Top customers for the month based on sales
    service_performances: list[ServicePerformance] # Top products for the month based on sales
    job_order_sales: list[JobOrderSales] # List of job orders for the month with their payment data
    miscellaneous_sales_list: list[MiscSalePublic] # List of miscellaneous sales for the month
    expenses_list: list[ExpensePublic] # List of expenses for the month