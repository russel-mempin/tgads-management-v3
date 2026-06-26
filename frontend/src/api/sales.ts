import type { MiscSale } from "@/types/sales";
import http from './http'

export async function getAllMiscSales() {
	const res = await http.get('/sales/')
	return res.data
}

export async function createMiscSale(payload: MiscSale) {
	const res = await http.post('/sales/', payload)
	return res.data
}

export async function updateMiscSale(id: string, payload: MiscSale) {
	const res = await http.patch(`/sales/${id}`, payload)
	return res.data
}

export async function archiveMiscSale(id: string) {
	const res = await http.patch(`/sales/${id}/archive`)
	return res.data
}