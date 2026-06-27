import type { Expense } from '@/types/expenses'
import http from './http'

export async function getAllExpenses() {
  const res = await http.get('/expenses/')
  return res.data
}

export async function createExpense(payload: Expense) {
  const res = await http.post('/expenses/', payload)
  return res.data
}

export async function updateExpense(id: string, payload: Expense) {
  const res = await http.patch(`/expenses/${id}`, payload)
  return res.data
}

export async function archiveExpense(id: string) {
  const res = await http.patch(`/expenses/${id}/archive`)
  return res.data
}
