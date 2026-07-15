<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { loginBackend } from '@/api/users'

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

const username = ref('')
const password = ref('')
const showPassword = ref(false)

const login = async () => {
    try {
        const data = await loginBackend(username.value, password.value)
        auth.login(data.access_token, data.first_name, data.last_name, data.role, data.is_superAdmin)
        router.push('/dashboard')
    } catch (error: any) {
        console.error(error.response?.data || error)
        toast.add({
            title: 'Login Failed',
            description: error.response?.data?.detail ?? 'An error occurred. Please try again.',
            icon: 'i-lucide-calendar-days',
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
                <UInput v-model="username" placeholder="Enter your username" fluid />
            </div>
            <div class="flex flex-col gap-1">
                <label class="font-medium text-slate-700">Password</label>
                <UInput v-model="password" placeholder="Enter your password" :type="showPassword ? 'text' : 'password'"
                    :ui="{ trailing: 'pe-1' }">
                    <template #trailing>
                        <UButton color="neutral" variant="link" size="sm"
                            :icon="showPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                            :aria-label="showPassword ? 'Hide password' : 'Show password'" :aria-pressed="showPassword"
                            aria-controls="password" @click="() => { showPassword = !showPassword }" />
                    </template>
                </UInput>
            </div>
            <UButton type="submit" label="Login" size="lg" trailing-icon="i-lucide-log-in" block :ui="{
                base: 'relative',
                trailingIcon: 'absolute inset-e-3'
            }" />
        </form>
    </div>
</template>