<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { User } from '@/types/users';
import { getAllUsers, archiveUser } from '@/api/users';
import { Button, DataTable, Column, useConfirm, useToast, ConfirmDialog, Tag } from 'primevue';
import { Plus, Info } from '@lucide/vue';
import UserForm from '@/components/UserForm.vue';
import HeaderTitle from '@/components/HeaderTitle.vue';

const confirm = useConfirm();
const toast = useToast();
const usersList = ref<User[]>([]);
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
const confirmDelete = (id: string) => {
	confirm.require({
		message: 'Do you want to delete this service?',
		header: 'Danger Zone',
		icon: 'pi pi-info-circle',
		rejectLabel: 'Cancel',
		rejectProps: {
			label: 'Cancel',
			severity: 'secondary',
			outlined: true
		},
		acceptProps: {
			label: 'Delete',
			severity: 'danger'
		},
		accept: async () => {
			await archiveUser(id)
			await fetchUsers();
			toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Service deleted', life: 3000 });
		},
		reject: () => {
			toast.add({ severity: 'error', summary: 'Cancelled', detail: 'You have cancelled', life: 3000 });
		}
	});
}
</script>

<template>
	<UserForm v-model:isVisible="isVisible" @saved="fetchUsers" :editData="editingData" @update:isVisible="onClose" />
	<ConfirmDialog>
		<template #icon>
			<Info class="w-10 h-10 text-red-500" />
		</template>
	</ConfirmDialog>
	<div class="mx-12 my-6 flex flex-col h-full min-h-0 overflow-hidden">
		<section class="flex justify-between items-center">
			<HeaderTitle
				title="Manage Users"
				subtitle="Manage access to the system and user information."
			/>
			<Button label="Add User" @click="isVisible = true">
				<template #icon>
					<Plus />
				</template>
			</Button>
		</section>
		<section class="mt-6 flex-1 h-full rounded-md border border-slate-300 overflow-hidden bg-white">
			<DataTable scrollable scroll-height="flex" :pt="{ root: 'h-full' }" :value="usersList" dataKey="id"
				tableStyle="min-width: 60rem;" paginator :rows="50" :rowsPerPageOptions="[5, 10, 20, 50]">
				<Column header="Name">
					<template #body="{ data }">
						<p>{{ data.first_name }} {{ data.last_name }}</p>
					</template>
				</Column>
				<Column field="username" header="Username" />
				<Column field="email" header="Email" />
				<Column field="role" header="Role" />
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
							<Button class="w-20" label="Delete" severity="danger" @click="confirmDelete(data.id)" />
						</div>
					</template>
				</Column>
			</DataTable>
		</section>
	</div>
</template>