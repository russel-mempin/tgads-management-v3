import type { MiscSaleCreate, MiscSaleUpdate } from '@/types/miscSale'
import type { DATE_PERIODS } from '@/utils/constants'
import http from './http'

export const getAllMiscSales = async (
    includeArchived = false,
    search?: string,
    datePeriod: DATE_PERIODS = 'all',
    offset = 0,
    limit = 20,
) => {
    const res = await http.get('/misc-sales/', {
        params: {
            include_archived: includeArchived,
            search: search || undefined,
            date_period: datePeriod,
            offset,
            limit,
        },
    })

    return res.data
}

export const getMiscSalesCount = async (
    includeArchived = false,
    search?: string,
    datePeriod: DATE_PERIODS = 'all',
) => {
    const res = await http.get('/misc-sales/count', {
        params: {
            include_archived: includeArchived,
            search: search || undefined,
            date_period: datePeriod,
        },
    })

    return res.data
}

export const createMiscSale = async (payload: MiscSaleCreate) => {
    const res = await http.post('/misc-sales/', payload)
    return res.data
}

export const updateMiscSale = async (misc_sale_id: string, payload: MiscSaleUpdate) => {
    const res = await http.patch(`/misc-sales/${misc_sale_id}`, payload)
    return res.data
}

export const archiveMiscSale = async (misc_sale_id: string) => {
    const res = await http.patch(`/misc-sales/${misc_sale_id}/archive`)
    return res.data
}