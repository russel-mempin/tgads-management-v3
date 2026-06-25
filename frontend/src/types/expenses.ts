export interface Expense {
  is_archived?: Boolean
  category: string
  amount: number
  date: Date
  description: string
  id?: string
}