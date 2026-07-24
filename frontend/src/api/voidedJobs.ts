import http from './http'

export const getAllVoidedJobs = async() => {
    const res = await http.get('/voided-jobs/')
    return res.data
}