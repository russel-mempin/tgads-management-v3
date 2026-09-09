import http from './http'
import type { ExpensePeriod } from '@/types/expense'

export const getAllExpenses = async (
    period: ExpensePeriod = 'all',
    includeArchived = false,
    offset = 0,
    limit = 100,
) => {
    const res = await http.get('/expenses/', {
        params: {
            period,
            include_archived: includeArchived,
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