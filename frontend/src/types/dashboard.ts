export interface AccountData {
    account_name: string;
    current_balance: string;
}

export interface ServiceSales {
    service_abbreviation: string;
    amount: string;
}

export interface OwnerDashboard {
    accounts_balances: AccountData[];
    collections_today: string;
    collections_this_month: string;
    outstanding_receivables: string;
    expenses_this_month: string;
    sales_per_service: ServiceSales[];
    overdue_jobs: number;
    pending_jobs: number;
}