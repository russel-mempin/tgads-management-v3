import http from './http'

export async function getCustomerNames() {
	const res = await http.get('/customers/names')
	return res.data
}

export async function getCustomerInfo(name: string) {
	const res = await http.get(`/customers/${name}`)
	return res.data
}