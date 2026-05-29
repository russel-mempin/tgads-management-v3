import type { ServiceCreate } from '@/types/services'
import http from './http'

export async function getAllServices() {
	const res = await http.get('/services/')
	return res.data
}

export async function getAllExtras() {
	const res = await http.get('/services/extras')
	return res.data
}

export async function createService(payload: ServiceCreate) {
	const res = await http.post('/services/', payload)
	return res.data
}

export async function editService(id: string, payload: ServiceCreate) {
	const res = await http.patch(`/services/${id}`, payload)
	return res.data
}

export async function archiveService(id: string) {
    const res = await http.patch(`/services/${id}/archive`)
    return res.data
}

export async function archiveExtraService(id: string) {
	const res = await http.patch(`/services/extras/${id}/archive`)
	return res.data
}