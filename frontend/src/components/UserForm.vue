<script setup lang="ts">
import type { User, UserCreate } from '@/types/users';
import { ref, watch, computed } from 'vue';
import { Button, Dialog, InputText, Password, Select } from 'primevue';
import { useToast } from 'primevue';
import { X, Check } from '@lucide/vue';
import { createUser } from '@/api/users';
import { useAuthStore } from '@/stores/auth';

const toast = useToast()
const authStore = useAuthStore()

const props = defineProps<{
	isVisible: boolean
	editData?: User | null
}>()

const emit = defineEmits<{
	(e: 'update:isVisible', value: boolean): void
	(e: 'saved'): void
}>()

const user = ref<UserCreate>({
	first_name: '',
	last_name: '',
	username: '',
	password: '',
	email: '',
	role: 'User',
	is_superAdmin: false,
	is_active: true,
});

const visibleRoles = computed(() => {
	if (authStore.isSuperuser || authStore.isOwner) return ['User', 'Admin', 'Owner']  // superuser & owner sees all
	if (authStore.isAdmin) return ['User'] // admin can only create Users
	return []
})

const resetData = () => {
	user.value = {
		first_name: '',
		last_name: '',
		username: '',
		password: '',
		email: '',
		role: 'User',
		is_superAdmin: false,
		is_active: true,
	}
}

watch(() => props.editData, (newData) => {
	if (newData) {
		user.value = { ...newData }
	} else {
		resetData()
	}
})

watch(
	() => [user.value.first_name, user.value.last_name],
	([first, last]) => {
		if (!props.editData) {
			user.value.username = `${(first ?? '').toLowerCase()}.${(last ?? '').toLowerCase()}`.replace(/\s/g, '')
		}
	}
)

const onSave = async () => {
	try {
		if (props.editData) {
			// await editExtra(props.editData.id, user.value)
		} else {
			await createUser(user.value)
		}
		toast.add({ severity: 'success', summary: 'Saved', detail: 'Data saved successfully.', life: 3000 })
		emit('saved')
		emit('update:isVisible', false)
		resetData()
	} catch (error: any) {
		console.error(error.response?.data || error)
		toast.add({
			severity: 'error',
			summary: 'Saving failed',
			detail: error.response?.data?.detail ?? 'An error occurred. Please try again.',
			life: 3000,
		})
	}
}
</script>
<template>
	<Dialog :visible="isVisible" @update:visible="emit('update:isVisible', $event)" modal
		:header="editData ? 'Edit User' : 'Add User'" :style="{ width: '40rem' }">
		<p class="text-gray-500 font-medium mb-4">Fields marked with<span class="text-red-500 font-semiold"> *
			</span>are
			required.</p>
		<div class="grid grid-cols-2 gap-4">
			<div class="flex flex-col mb-4">
				<label class="font-semibold mb-1">First Name<span class="text-red-500 font-semibold"> *</span></label>
				<InputText v-model="user.first_name" />
			</div>
			<div class="flex flex-col mb-4">
				<label class="font-semibold mb-1">Last Name<span class="text-red-500 font-semibold"> *</span></label>
				<InputText v-model="user.last_name" />
			</div>
		</div>
		<div class="flex flex-col mb-4">
			<div class="mb-1">
				<label class="font-semibold">Username&nbsp;&nbsp;</label>
				<span
					class="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-500">Auto-generated</span>
			</div>
			<InputText v-model="user.username" disabled />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Password<span class="text-red-500 font-semibold"> *</span></label>
			<Password v-model="user.password" fluid />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Email<span class="text-red-500 font-semibold"> *</span></label>
			<InputText v-model="user.email" />
		</div>
		<div class="grid grid-cols-2 gap-4">
			<div class="flex flex-col mb-4">
				<label class="font-semibold mb-1">Role<span class="text-red-500 font-semibold"> *</span></label>
				<Select v-model="user.role" :options="visibleRoles" />
			</div>
			<div class="flex flex-col mb-4">
				<div class="flex flex-col mb-4">
					<label class="font-semibold mb-1">Active<span class="text-red-500 font-semibold"> *</span></label>
					<div class="pill-toggle" :class="user.is_active ? 'on' : 'off'"
						@click="user.is_active = !user.is_active">
						<div class="pill-icon" :class="{ active: !user.is_active }">
							<X :size="16" />
						</div>
						<div class="pill-icon" :class="{ active: user.is_active }">
							<Check :size="16" />
						</div>
					</div>
				</div>
			</div>
		</div>
		<div v-if="authStore.isSuperuser" class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Superuser</label>
			<div class="pill-toggle" :class="user.is_superAdmin ? 'on' : 'off'"
				@click="user.is_superAdmin = !user.is_superAdmin">
				<div class="pill-icon" :class="{ active: !user.is_superAdmin }">
					<X :size="16" />
				</div>
				<div class="pill-icon" :class="{ active: user.is_superAdmin }">
					<Check :size="16" />
				</div>
			</div>
		</div>
		<div class="flex justify-end gap-2">
			<Button class="w-20" label="Cancel" severity="secondary" @click="emit('update:isVisible', false)" />
			<Button class="w-20" label="Save" @click="onSave" />
		</div>
	</Dialog>
</template>

<style scoped>
.pill-toggle {
	display: flex;
	align-items: center;
	border: 2px solid;
	border-radius: 10px;
	padding: 4px;
	cursor: pointer;
	width: 100%;
	transition: border-color 0.2s;
}

.pill-icon {
	flex: 1;
	height: 32px;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	color: var(--color-text-secondary);
	transition: background 0.2s, color 0.2s;
}

.pill-toggle.on {
	border-color: #22c55e;
}

.pill-toggle.off {
	border-color: #ef4444;
}

.pill-toggle.on .pill-icon.active {
	background: #22c55e;
	color: white;
}

.pill-toggle.off .pill-icon.active {
	background: #ef4444;
	color: white;
}
</style>