import http from './http'
import type { JobOrders } from '@/types/job_orders'

export async function getAllJobOrders() {
	const res = await http.get('/job-orders/')
	return res.data
}
