import http from './http'
import type { TransferCreate } from '@/types/transfer'

export const getAllTransfers = async (
    includeArchived = false,
    search?: string,
) => {
    const res = await http.get('/transfers/', {
        params: {
            include_archived: includeArchived,
            search: search || undefined
        }
    })
    return res.data
}

export const createTransfer = async (payload: TransferCreate) => {
    const res = await http.post('/transfers/', payload)
    return res.data
}