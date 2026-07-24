import http from './http'

export const getAllForReview = async() => {
    const res = await http.get('/for-reviews/')
    return res.data
}

export const getForReviewCount = async() => {
    const res = await http.get('/for-reviews/count')
    return res.data
}