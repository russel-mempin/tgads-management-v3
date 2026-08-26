import type { UnlinkedPayment } from '@/types/forReview'
import http from './http'

export const getAllForReview = async () => {
    const res = await http.get('/for-reviews/')
    return res.data
}

export const getForReviewCount = async () => {
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

export const searchPossibleJobOrders = async (entity_id: string, search_value: string) => {
    const res = await http.get(
        `/for-reviews/payments/${entity_id}/possible-job-orders/search`,
        {
            params: {
                search_value,
            },
        },
    )
    return res.data
}

export const assignPaymentDataToJob = async (entity: UnlinkedPayment, match_id: string) => {
    const res = await http.post(`/for-reviews/payments/${entity.id}/`, entity, { params: { match_id: match_id } })
    return res.data
}