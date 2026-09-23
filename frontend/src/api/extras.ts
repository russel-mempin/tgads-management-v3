import http from './http'

export const getAllExtras = async() => {
	const res = await http.get('/extras/')
	return res.data
}