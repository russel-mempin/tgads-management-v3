export type ExpensePeriod =
    | 'today'
    | 'this_week'
    | 'this_month'
    | 'last_month'
    | 'this_year'
    | 'all'

export type ExpenseCategory = 
    | 'Food'
    | 'Maintenance'
    | 'Utilities'
    | 'Transportation'
    | 'Supplies'
    | 'Payroll'
    | 'Benefits'
    | 'Production'
    | 'Miscellaneous'
    | 'Equipment'

interface ExpenseBase {
    date: string
    category: ExpenseCategory
    description: string
}

export interface Expense extends ExpenseBase {
    id?: string
    amount: string
    account_id?: string
    account_name: string
}

export interface ExpenseCreate extends ExpenseBase {
    amount: number
    fund_source: string
}

export interface ExpenseSummary {
    total: string
    count: number
    largest: Expense | null
}

export interface ExpenseByCategory {
    category: string
    amount: string
}

export interface ExpenseList {
    items: Expense[]
    total_items: number
    summary: ExpenseSummary
    expense_by_category: ExpenseByCategory[]
}