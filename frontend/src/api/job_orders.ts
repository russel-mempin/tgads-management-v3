import http from './http'

export async function getAllJobOrders() {
	const res = await http.get('/job-orders/')
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
