import http from './http'
import type { DATE_PERIODS, TRANSACTION_CATEGORIES } from '@/utils/constants'

export const getAllTransactions = async (
    period: DATE_PERIODS = 'all',
    category?: TRANSACTION_CATEGORIES,
    offset = 0,
    limit = 100,
) => {
    const res = await http.get('/transactions/', {
        params: {
            period,
            category,
            offset,
            limit
        }
    })
    return res.data
}