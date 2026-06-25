import type { Expense } from "@/types/expenses";
import http from './http'

export async function getAllExpenses() {
	const res = await http.get('/expenses/')
	return res.data
}