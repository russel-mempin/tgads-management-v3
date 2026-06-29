<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import type { User } from '@/types/users';
import { getAllUsers } from '@/api/users';
import { Button, DataTable, Column, Tag } from 'primevue';
import { Plus, Info } from '@lucide/vue';
import UserForm from '@/components/UserForm.vue';
import HeaderTitle from '@/components/HeaderTitle.vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore()
const usersList = ref<User[]>([]);
const visibleUsers = computed(() => {
	if (authStore.isSuperuser) return usersList.value  // superuser sees everything
	return usersList.value.filter(u => {
		if (u.is_superAdmin) return false
		if (u.role === 'Owner' && !authStore.isOwner) return false
		return true
	})
})
const fetchUsers = async () => {
	usersList.value = await getAllUsers()
	console.log(usersList.value)
}
onMounted(async () => {
	fetchUsers()
});
const isVisible = ref(false);
const editingData = ref<User | null>(null)
const openEdit = (data: User) => {
	editingData.value = data
	isVisible.value = true
}
const onClose = () => {
	editingData.value = null
	isVisible.value = false
}
</script>

<template>
	<UserForm v-model:isVisible="isVisible" @saved="fetchUsers" :editData="editingData" @update:isVisible="onClose" />
	<div class="mx-12 my-6 flex flex-col h-full min-h-0 overflow-hidden">
		<section class="flex justify-between items-center">
			<HeaderTitle title="Manage Users" subtitle="Manage access to the system and user information." />
			<Button label="Add User" @click="isVisible = true">
				<template #icon>
					<Plus />
				</template>
			</Button>
		</section>
		<section class="mt-6 flex-1 h-full rounded-md border border-slate-300 overflow-hidden bg-white">
			<DataTable scrollable scroll-height="flex" :pt="{ root: 'h-full' }" :value="visibleUsers" dataKey="id"
				tableStyle="min-width: 60rem;" paginator :rows="50" :rowsPerPageOptions="[5, 10, 20, 50]">
				<Column header="Name">
					<template #body="{ data }">
						<p>{{ data.first_name }} {{ data.last_name }}</p>
					</template>
				</Column>
				<Column field="username" header="Username" />
				<Column field="email" header="Email" />
				<Column field="role" header="Access Level" />
				<Column v-if="authStore.isSuperuser" field="is_superAdmin" header="Super Admin">
					<template #body="{ data }">
						<Tag :value="data.is_superAdmin ? 'Yes' : 'No'"
							:severity="data.is_superAdmin ? 'success' : 'secondary'" />
					</template>
				</Column>
				<Column field="is_active" header="Active">
					<template #body="{ data }">
						<Tag :value="data.is_active ? 'Yes' : 'No'"
							:severity="data.is_active ? 'success' : 'secondary'" />
					</template>
				</Column>
				<Column style="width: 1rem">
					<template #body="{ data }">
						<div class="flex gap-4">
							<Button class="w-20" label="Edit" severity="warn" @click="openEdit(data)" />
						</div>
					</template>
				</Column>
			</DataTable>
		</section>
	</div>
</template>