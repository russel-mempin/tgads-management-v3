import http from './http'
import type { JobItemCreate } from '@/types/jobOrder'

export const getAllForReview = async (offset = 0, limit = 100) => {
  const res = await http.get('/for-reviews/', {
    params: { offset, limit },
  })
  return res.data
}

export const getForReviewCount = async () => {
  const res = await http.get('/for-reviews/count')
  return res.data
}

export const getPaymentForReviewDetails = async (payment_id: string) => {
  const res = await http.get(`/for-reviews/payments/${payment_id}`)
  return res.data
}

export const searchPossibleJobOrders = async (payment_id: string, search_value: string) => {
  const res = await http.get(`/for-reviews/payments/${payment_id}/possible-job-orders/search`, {
    params: {
      search_value,
    },
  })
  return res.data
}

export const assignPaymentDataToJob = async (payment_id: string, match_id: string) => {
  const res = await http.post(`/for-reviews/payments/${payment_id}/job-assign`, null, {
    params: { match_id: match_id },
  })
  return res.data
}

export const assignPaymentDataToMisc = async (payment_id: string) => {
  const res = await http.post(`/for-reviews/payments/${payment_id}/misc-assign`)
  return res.data
}

export const getJobForReviewDetails = async (job_order_id: string) => {
  const res = await http.get(`/for-reviews/job-orders/${job_order_id}`)
  return res.data
}

export const updateWholeJobItem = async (
  job_order_id: string,
  job_item_id: string,
  data: JobItemCreate,
) => {
  const res = await http.put(
    `/for-reviews/job-orders/${job_order_id}/job-items/${job_item_id}`,
    data,
  )
  return res.data
}

export const voidJobOrderAndDeleteReview = async (reason: string, job_order_id: string) => {
  const res = await http.patch(`/for-reviews/job-orders/${job_order_id}/void`, null, { params: { reason } })
  return res.data
}

export const getJobItemWithJobOrder = async(job_item_id: string) => {
  const res = await http.get(`/for-reviews/job-items/${job_item_id}`)
  return res.data 
}

export const markJobOrderAsResolved = async(job_order_id: string) => {
  const res = await http.patch(`/for-reviews/job-orders/${job_order_id}/resolve`)
  return res.data
}