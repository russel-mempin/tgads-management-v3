import http from './http'
import type { ExpenseCategory, ExpensePeriod, ExpenseCreate } from '@/types/expense'

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