import http from './http'
import type { JobOrderCreate, JobItem, JobItemCreate, JobItemUpdate, PricingData } from '@/types/jobOrder'

export async function getJobOrderKpis() {
	const res = await http.get('/job-orders/kpis')
	return res.data
}

export const getAllJobOrders = async (params: {
    offset?: number
    limit?: number
    payment_status?: string
    job_status?: string
    search?: string
    filter?: string
} = {}) => {
    const response = await http.get('/job-orders/', { params })
    return response.data
}

export const getJobOrderCount = async (params: {
	payment_status?: string
	job_status?: string
	search?: string
} = {}) => {
	const response = await http.get('/job-orders/count', { params })
	return response.data
}

export async function getJobOrder(job_order_id: string) {
	const res = await http.get(`/job-orders/${job_order_id}`)
	return res.data
}

export const getUnitPrice = async (params: {
  height?: number
  width?: number
  service_id: string
  option_id: string
  size_unit?: string
  quantity: number
}): Promise<PricingData> => {
  const response = await http.get<PricingData>('/job-orders/compute-unit-price', {
    params
  })

  return response.data
}

export const createJobOrder = async(payload: JobOrderCreate) => {
  const res = await http.post('/job-orders/', payload)
  return res.data
}

export const createJobItem = async(payload: JobItemCreate, job_order_id: string): Promise<JobItem> => {
  const res = await http.post(`/job-orders/job-items/${job_order_id}`, payload)
  return res.data
}

export const updateJobItem = async (payload: JobItemUpdate, id: string): Promise<JobItem> => {
  const res = await http.patch(`/job-orders/job-items/${id}`, payload)
  return res.data
}