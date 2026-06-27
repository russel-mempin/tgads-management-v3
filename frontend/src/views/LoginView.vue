<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { loginBackend } from '@/api/users'
import { useToast } from 'primevue/usetoast'
import { InputText, Password, Button } from 'primevue'

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

const username = ref('')
const password = ref('')

const login = async () => {
    try {
        const data = await loginBackend(username.value, password.value)
        auth.login(data.access_token, data.first_name, data.last_name, data.role, data.is_superAdmin)
        router.push('/dashboard')
    } catch (error: any) {
        console.error(error.response?.data || error)
        toast.add({
            severity: 'error',
            summary: 'Login Failed',
            detail: error.response?.data?.detail ?? 'An error occurred. Please try again.',
            life: 3000,
        })
    }
}
</script>

<template>
    <div class="px-10 py-8 rounded-md">
        <div class="mb-8">
            <h1 class="text-2xl text-slate-600 font-semibold">Welcome back!</h1>
            <p>Sign in to start managing job order data.</p>
        </div>
        <form @submit.prevent="login" class="flex flex-col gap-4">
            <div class="flex flex-col gap-1">
                <label class="font-medium text-slate-700">Username</label>
                <InputText v-model="username" placeholder="Enter your username" fluid />
            </div>
            <div class="flex flex-col gap-1">
                <label class="font-medium text-slate-700">Password</label>
                <Password v-model="password" placeholder="Enter your password" fluid :feedback="false" toggleMask />
            </div>
            <Button type="submit" label="Login" class="mt-4" fluid />
        </form>
    </div>
</template>