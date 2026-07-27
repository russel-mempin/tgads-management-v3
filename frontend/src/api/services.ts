import http from './http'

export const getAllServices = async() => {
	const res = await http.get('/services/')
	return res.data
}