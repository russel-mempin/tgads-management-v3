interface PaymentEntry {
  id: string
  date_received: Date
  reference_number: string
  method: string
  amount: number
  customer_name: string
  jo_number: number
}

interface ExpenseEntry {
  id: string
  date: Date
  category: string
  amount: number
  description: string
  is_archived: boolean
}

export interface DailyReport {
  date: Date
  cash_payments: PaymentEntry[]
  cheque_payments: PaymentEntry[]
  gcash_payments: PaymentEntry[]
  expenses: ExpenseEntry[]
  total_cash: number
  total_cheque: number
  total_gcash: number
  total_sales: number
  total_expenses: number
  ending_balance: number
}
