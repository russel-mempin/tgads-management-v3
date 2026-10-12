import http from './http'
import type { ExpenseCategory, ExpensePeriod, ExpenseCreate, ExpenseUpdate } from '@/types/expense'

export const getAllExpenses = async (
    period: ExpensePeriod = 'all',
    includeArchived = false,
    category?: ExpenseCategory,
    search?: string,
    offset = 0,
    limit = 100,
) => {
    const res = await http.get('/expenses/', {
        params: {
            period,
            include_archived: includeArchived,
            category,
            search,
            offset,
            limit,
        },
    })

    return res.data
}

export const getExpenseCount = async() => {
    const res = await http.get('/expenses/count')
    return res.data
}

export const createExpense = async (payload: ExpenseCreate) => {
    const res = await http.post('/expenses/', payload)
    return res.data
}

export const archiveExpense = async (expenseId: string) => {
    const res = await http.patch(`/expenses/${expenseId}/archive`)
    return res.data
}

export const updateExpense = async (expenseId: string, payload: ExpenseUpdate) => {
    const res = await http.patch(`/expenses/${expenseId}`, payload)
    return res.data
}