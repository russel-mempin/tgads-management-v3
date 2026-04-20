import http from './http'

export async function getAllServices() {
	const res = await http.get('/services/')
	return res.data
}