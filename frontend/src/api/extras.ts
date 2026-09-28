import http from './http'
import type { ExtraCreate, ExtraUpdate } from '@/types/extra'

export const getAllExtras = async() => {
	const res = await http.get('/extras/')
	return res.data
}

export const createExtra = async(extra: ExtraCreate) => {
	const res = await http.post('/extras/', extra)
	return res.data
}

export const updateExtra = async(extra_id: string, extra_data: ExtraUpdate) => {
	const res = await http.patch(`/extras/${extra_id}`, extra_data)
	return res.data
}