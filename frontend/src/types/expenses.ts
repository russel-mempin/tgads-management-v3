export interface Expense {
  date: Date
  category: string
  amount: number
  description: string
  is_archived: Boolean
  id: string
  account_name: string
}

export interface ExpenseCreate {
  date: Date
  category: string
  amount: number
  fund_source: string
  description: string
  id?: string
}