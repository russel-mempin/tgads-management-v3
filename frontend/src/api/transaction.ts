import http from './http'
import type { DATE_PERIODS, TRANSACTION_CATEGORIES } from '@/utils/constants'

export const getAllTransactions = async (
    period: DATE_PERIODS = 'all',
    category?: TRANSACTION_CATEGORIES,
    method?: string,
    offset = 0,
    limit = 100,
) => {
    const res = await http.get('/transactions/', {
        params: {
            period,
            category,
            account_id: method,
            offset,
            limit
        }
    })
    return res.data
}