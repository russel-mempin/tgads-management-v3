import http from './http'
import type { JobOrder, JobOrderCreate } from '@/types/job_orders'

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

export async function getJobOrder(jo_number: number) {
	const res = await http.get(`/job-orders/${jo_number}`)
	return res.data
}

export async function computePrice(height: number, width: number, service_name: string, size_unit: string) {
	const res = await http.get('/job-orders/compute-unit-price', {
		params: {
			height,
			width,
			service_name,
			size_unit,
    	},
	})
	return res.data
}

export async function createJobOrder(payload: JobOrderCreate) {
	const res = await http.post('/job-orders/', payload)
	return res.data
}

export async function archiveJobOrder(jo_number: number) {
	const res = await http.patch(`/job-orders/${jo_number}/archive`)
	return res.data
}

export async function editJobOrder(jo_number: number, payload: JobOrderCreate) {
	const res = await http.put(`/job-orders/${jo_number}`, payload)
	return res.data
}

export async function getJobOrderKpis() {
	const res = await http.get('/job-orders/kpis')
	return res.data
}