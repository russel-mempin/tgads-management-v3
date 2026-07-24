import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router/index'
import { useForReviewCount } from '@/stores/forReviewCounter'

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

    const login = async (token: string, first_name: string, last_name: string, role: User['role'], is_superAdmin: boolean) => {
        user.value = { role, token, first_name, last_name, is_superAdmin }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(user.value))
        if (['Admin', 'Owner'].includes(role)) {
            const reviewStore = useForReviewCount()
            await reviewStore.fetchCount()
        }
    }

    const initialize = async () => {
        if (!user.value) return

        if (['Admin', 'Owner'].includes(user.value.role)) {
            const reviewStore = useForReviewCount()
            await reviewStore.fetchCount()
        }
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
        initialize,
        login,
        logout,
    }
})