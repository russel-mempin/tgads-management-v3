import type { Expense } from "./expense"
import type { MiscSale } from "./miscSale"

export interface CustomerPerformance {
    name: string
    order_quantity: number
    sales: string
    balance: string
    last_order: string
    sales_percentage: number
}

export interface ProductPerformance {
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
    ending_balance: string
}

export interface MonthlyPerformanceBase {
    month: string
    collected: string
    expenses: string
    net: string
    sales: string
    receivables: string
}

export interface MonthlyPerformance {
    total_of_accounts: string
    customer_performances: CustomerPerformance[]
    product_performances: ProductPerformance[]
    job_order_sales: JobOrderSales[]
    miscellaneous_sales: MiscSale[]
    expenses_list: Expense[]
}