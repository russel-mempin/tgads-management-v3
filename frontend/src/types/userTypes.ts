export interface UserCreate {
	first_name: string
	last_name: string
	username: string
	password: string
	email: string
	role: string
	is_superAdmin: boolean
	is_active: boolean
}

export interface User extends UserCreate {
	id: string
}