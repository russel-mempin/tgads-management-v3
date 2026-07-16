import http from './http'

export async function getJobOrderKpis() {
	const res = await http.get('/job-orders/kpis')
	return res.data
}