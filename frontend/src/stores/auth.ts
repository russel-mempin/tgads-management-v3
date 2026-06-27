import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router/index'

type User = {
    role: 'User' | 'Admin' | 'Owner'
    token: string
    first_name: string
    last_name: string
    is_superAdmin: boolean
}

const STORAGE_KEY = 'auth_user'

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(
        JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
    )

    const login = (token: string, first_name: string, last_name: string, role: User['role'], is_superAdmin: boolean) => {
        user.value = { role, token, first_name, last_name, is_superAdmin }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(user.value))
    }

    const logout = () => {
        user.value = null
        localStorage.removeItem(STORAGE_KEY)
        router.replace('/')
    }

    const isLoggedIn = computed(() => user.value !== null)
    const isAdmin = computed(() => ['Admin', 'Owner'].includes(user.value?.role ?? ''))
    const isOwner = computed(() => user.value?.role === 'Owner')
    const isSuperuser = computed(() => user.value?.is_superAdmin === true)

    return {
        user,
        isLoggedIn,
        isAdmin,
        isOwner,
        isSuperuser,
        login,
        logout,
    }
})