import type { MiscSaleCreate, MiscSaleUpdate } from '@/types/miscSale'
import http from './http'

export const getAllMiscSales = async(includeArchived = false) => {
    const res = await http.get('/misc-sales/', {
        params: {
            include_archived: includeArchived
        }
    })
    return res.data
}

export const createMiscSale = async(payload: MiscSaleCreate) => {
    const res = await http.post('/misc-sales/', payload)
    return res.data
}

export const updateMiscSale = async(misc_sale_id: string, payload: MiscSaleUpdate) => {
    const res = await http.patch(`/misc-sales/${misc_sale_id}`, payload)
    return res.data
}