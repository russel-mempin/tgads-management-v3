import http from './http'

export async function getAllServices() {
	const res = await http.get('/services/')
	return res.data
}

export async function getAllExtras() {
	const res = await http.get('/services/extras')
	return res.data
}