import http from './http'

export const getAllForReview = async() => {
    const res = await http.get('/for-reviews/')
    return res.data
}