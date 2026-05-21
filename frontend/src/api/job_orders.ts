import http from './http'
import type { JobOrderCreate } from '@/types/job_orders'

export async function getAllJobOrders() {
	const res = await http.get('/job-orders/')
	return res.data
}

export async function getJobOrder(jo_number: string) {
	const res = await http.get(`/job-orders/${jo_number}`)
	return res.data
}

export async function computePrice(height: number, width: number, service_name: string) {
	const res = await http.get('/job-orders/compute-unit-price', {
		params: {
			height,
			width,
			service_name,
    	},
	})
	return res.data
}

export async function createJobOrder(payload: JobOrderCreate) {
	const res = await http.post('/job-orders/', payload)
	return res.data
}