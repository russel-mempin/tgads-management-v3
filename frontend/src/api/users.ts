import http from './http'
import type { UserCreate } from '@/types/user'

export async function loginBackend(username: string, password: string) {
	const data = new URLSearchParams()
	data.append('username', username)
	data.append('password', password)

	const res = await http.post('/users/token', data, {
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded'
		}
	})

	return res.data
}

export async function getAllUsers() {
	const res = await http.get('/users/')
	return res.data
}

export async function createUser(payload: UserCreate) {
	const res = await http.post('users/', payload)
	return res.data
}