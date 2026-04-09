import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router  from '@/router/index'

type User = {
	role: 'admin' | 'user'
	token: string
}

const STORAGE_KEY = 'auth_user'

export const useAuthStore = defineStore('auth', () => {
	const user = ref<User | null>(
		JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
	)

	const loginAsAdmin = (token: string) => {
		user.value = { role: 'admin', token }
		localStorage.setItem(STORAGE_KEY, JSON.stringify(user.value))
	}

	const loginAsUser = (token: string) => {
		user.value = { role: 'user', token }
		localStorage.setItem(STORAGE_KEY, JSON.stringify(user.value))
	}

	const logout = () => {
		user.value = null
		localStorage.removeItem(STORAGE_KEY)
		router.replace('/')
	}

	const isAdmin = computed(() => user.value?.role === 'admin')
	const isLoggedIn = computed(() => user.value !== null)

	return {
		user,
		isAdmin,
		isLoggedIn,
		loginAsAdmin,
		loginAsUser,
		logout,
	}
})