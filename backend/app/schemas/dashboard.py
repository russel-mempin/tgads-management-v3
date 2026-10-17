from decimal import Decimal

from sqlmodel import SQLModel


class AccountData(SQLModel):
    account_name: str
    current_balance: Decimal

class ServiceSales(SQLModel):
    service_abbreviation: str
    amount: Decimal

class OwnerDashboard(SQLModel):
    accounts_balances: list[AccountData]
    collections_today: Decimal
    collections_this_month: Decimal
    outstanding_receivables: Decimal
    expenses_this_month: Decimal
    sales_per_service: list[ServiceSales]
    overdue_jobs: int
    pending_jobs: int
