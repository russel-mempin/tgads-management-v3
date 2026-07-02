import http from './http'

export async function getAccountOptions() {
	const res = await http.get('/accounts/options')
	return res.data
}