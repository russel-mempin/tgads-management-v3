import http from './http'
import type { JobItemCreate } from '@/types/jobOrder'

export const getAllForReview = async () => {
    const res = await http.get('/for-reviews/')
    return res.data
}

export const getForReviewCount = async () => {
    const res = await http.get('/for-reviews/count')
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

export const assignPaymentDataToJob = async (entity_id: string, match_id: string) => {
    const res = await http.post(`/for-reviews/payments/${entity_id}/job-assign`, null, { params: { match_id: match_id } })
    return res.data
}

export const assignPaymentDataToMisc = async (entity_id: string) => {
    const res = await http.post(`/for-reviews/payments/${entity_id}/misc-assign`)
    return res.data
}

export const getJobForReviewDetails = async (entity_id: string) => {
    const res = await http.get(`/for-reviews/job-orders/${entity_id}`)
    return res.data
}

export const updateWholeJobItem = async(job_order_id: string, job_item_id: string, data: JobItemCreate) => {
    const res = await http.put(`/for-reviews/job-orders/${job_order_id}/job-items/${job_item_id}`, data)
    return res.data
}