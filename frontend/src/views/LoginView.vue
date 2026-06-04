<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { loginBackend } from '@/api/users'
import { useToast } from 'primevue/usetoast'

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

const username = ref('')
const password = ref('')

const login = async () => {
	try {
		const data = await loginBackend(username.value, password.value)
		// store token + role
		if (data.role === 'Admin') {
			auth.loginAsAdmin(data.access_token, data.first_name, data.last_name)
		} else {
			auth.loginAsUser(data.access_token, data.first_name, data.last_name)
		}
		// redirect after login
		if (auth.isAdmin) {
			router.push('/admin/dashboard')
		} else {
			router.push('/user/dashboard')
		}
	}
	catch (error: any) {
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
			<input class="border border-slate-400 rounded-sm px-3 py-2 text-lg" v-model="username"
				placeholder="Username" />
			<input class="border border-slate-400 rounded-sm px-3 py-2 text-lg" v-model="password" type="password"
				placeholder="Password" />
			<button type="submit" class="mt-4 bg-blue-400 rounded-sm py-2 text-lg text-white">
				Login
			</button>
		</form>
	</div>
</template>
