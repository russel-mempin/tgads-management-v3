import http from './http'

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