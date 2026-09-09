export type ExpensePeriod =
    | 'today'
    | 'this_week'
    | 'this_month'
    | 'last_month'
    | 'this_year'
    | 'all'

interface ExpenseBase {
    date: string
    category: string
    description: string
}

export interface Expense extends ExpenseBase {
    id: string
    amount: string
    account_name: string
}

interface ExpenseSummary {
    total: string
    count: number
    largest: string
}

export interface ExpenseList {
    items: Expense[]
    summary: ExpenseSummary
}