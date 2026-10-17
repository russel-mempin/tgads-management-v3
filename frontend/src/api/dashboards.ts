import http from './http'

export const getOwnerDashboard = async() => {
    const res = await http.get('/dashboard/owner')
    return res.data
}