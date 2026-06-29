<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Button, DataTable, Column, useConfirm, useToast, ConfirmDialog } from 'primevue';
import { Plus, Info } from '@lucide/vue';
import HeaderTitle from '@/components/HeaderTitle.vue';
import SalesForm from '@/components/SalesForm.vue';
import { getAllMiscSales, archiveMiscSale } from '@/api/sales';
import type { MiscSale } from '@/types/sales';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore()
const confirm = useConfirm();
const toast = useToast();
const isVisible = ref(false);
const miscSalesList = ref<MiscSale[]>([]);
const editingData = ref<MiscSale | null>(null)

const fetchMiscSales = async () => {
	miscSalesList.value = await getAllMiscSales()
}
onMounted(async () => {
	fetchMiscSales()
});
const openEdit = (data: MiscSale) => {
	editingData.value = data
	isVisible.value = true
}
const onClose = () => {
	editingData.value = null
	isVisible.value = false
}
const confirmDelete = (id: string) => {
	confirm.require({
		message: 'Do you want to delete this data?',
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
			await archiveMiscSale(id)
			await fetchMiscSales();
			toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Data deleted', life: 3000 });
		},
		reject: () => {
			toast.add({ severity: 'error', summary: 'Cancelled', detail: 'You have cancelled', life: 3000 });
		}
	});
}
</script>

<template>
	<SalesForm v-model:is-visible="isVisible" @saved="fetchMiscSales" :edit-item="editingData" @update:is-visible="onClose" />
	<ConfirmDialog>
		<template #icon>
			<Info class="w-10 h-10 text-red-500" />
		</template>
	</ConfirmDialog>
	<div class="mx-12 my-6 flex flex-col h-full min-h-0 overflow-hidden">
		<section class="flex justify-between items-center">
			<HeaderTitle :title="authStore.isOwner ? 'Sales' : 'Daily Sales'" subtitle="Monitor sales including document printing and others without Job Orders." />
			<Button label="Add Misc. Sale" @click="isVisible = true">
				<template #icon>
					<Plus />
				</template>
			</Button>
		</section>
		<section class="mt-6 flex-1 h-full rounded-md border border-slate-300 overflow-hidden bg-white">
			<DataTable scrollable scroll-height="flex" :pt="{ root: 'h-full' }" :value="miscSalesList" dataKey="id"
				tableStyle="min-width: 60rem;" paginator :rows="50" :rowsPerPageOptions="[5, 10, 20, 50]">
				<Column field="date" header="Date">
					<template #body="{ data }">
						<p>{{ formatDate(data.date) }}</p>
					</template>
				</Column>
				<Column field="description" header="Description" />
				<Column field="amount" header="Amount">
					<template #body="{ data }">
						<p>{{ formatCurrency(data.amount) }}</p>
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