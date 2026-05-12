import http from './http'

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
