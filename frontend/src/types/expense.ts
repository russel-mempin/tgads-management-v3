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