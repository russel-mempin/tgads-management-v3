import http from './http'

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


export async function getJobOrder(jo_number: number) {
	const res = await http.get(`/job-orders/${jo_number}`)
	return res.data
}