import http from './http'

export const getAllMiscSales = async(includeArchived = false) => {
    const res = await http.get('/misc-sales/', {
        params: {
            include_archived: includeArchived
        }
    })
    return res.data
}