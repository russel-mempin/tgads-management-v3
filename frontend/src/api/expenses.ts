import http from './http'

export const getAllExpenses = async(includeArchived = false) => {
    const res = await http.get('/expenses/', {
        params: {
            include_archived: includeArchived
        }
    })
    return res.data
}