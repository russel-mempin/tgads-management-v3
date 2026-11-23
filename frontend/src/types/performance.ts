import type { Expense } from "./expense"
import type { MiscSale } from "./miscSale"
import type { Transaction } from "./transaction"

export interface CustomerPerformance {
    name: string
    order_quantity: number
    sales: string
    balance: string
    last_order: string
    sales_percentage: number
}

export interface ServicePerformance {
    full_product_name: string
    order_quantity: number
    material_consumed_in_sqft: string
    sales: string
    sales_percentage: number
}

export interface JobOrderSales {
    jo_number: number
    customer_name: string
    date_received: string
    total_due: string
    total_paid: string
    balance: string
}

export interface PerAccountCollections {
    account_name: string
    collections: string
    deductions: string
    ending_balance: string
}

export interface MonthlyPerformanceBase {
    month: number
    collected: string
    expenses: string
    net: string
    sales: string
    receivables: string
}

export interface MonthlyPerformance extends MonthlyPerformanceBase {
    snapshots_of_accounts: PerAccountCollections[]
    collected_list: Transaction[]
    customer_performances: CustomerPerformance[]
    service_performances: ServicePerformance[]
    job_order_sales: JobOrderSales[]
    miscellaneous_sales: MiscSale[]
    expenses_list: Expense[]
}