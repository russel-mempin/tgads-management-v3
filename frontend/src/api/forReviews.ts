import http from './http'

export const getAllForReview = async() => {
    const res = await http.get('/for-reviews/')
    return res.data
}

export const getForReviewCount = async() => {
    const res = await http.get('/for-reviews/count')
    return res.data
}

export const getJobForReviewDetails = async (entity_id: string) => {
    const res = await http.get(`/for-reviews/job-orders/${entity_id}`)
    return res.data
}

export const getPaymentForReviewDetails = async (entity_id: string) => {
    const res = await http.get(`/for-reviews/payments/${entity_id}`)
    return res.data
}