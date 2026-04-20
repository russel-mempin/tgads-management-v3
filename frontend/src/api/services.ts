import http from './http'

export async function getServiceNames() {
	const res = await http.get('/services/names')
	return res.data
}

export async function getServiceInfo(name: string) {
	const res = await http.get(`/services/${name}`)
	return res.data
}