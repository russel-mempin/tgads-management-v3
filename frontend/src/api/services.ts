import type { ServiceOptionCreate, ServiceOptionUpdate } from '@/types/service'
import http from './http'

export const getAllServices = async() => {
	const res = await http.get('/services/')
	return res.data
}

export const getServiceData = async(service_id: string) => {
	const res = await http.get(`/services/${service_id}`)
	return res.data
}

export const createOption = async(parent_service_id: string, option: ServiceOptionCreate) => {
	const res = await http.post(`/services/${parent_service_id}/options/`, option)
	return res.data
}

export const updateOption = async(parent_service_id: string, option_id: string, option: ServiceOptionUpdate) => {
	const res = await http.patch(`/services/${parent_service_id}/options/${option_id}`, option)
	return res.data
}