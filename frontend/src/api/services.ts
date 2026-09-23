import http from './http'

export const getAllServices = async() => {
	const res = await http.get('/services/')
	return res.data
}

export const getServiceData = async(service_id: string) => {
	const res = await http.get(`/services/${service_id}`)
	return res.data
}