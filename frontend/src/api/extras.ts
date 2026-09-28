import http from './http'
import type { ExtraCreate } from '@/types/extra'

export const getAllExtras = async() => {
	const res = await http.get('/extras/')
	return res.data
}

export const createExtra = async(extra: ExtraCreate) => {
	const res = await http.post('/extras/', extra)
	return res.data
}