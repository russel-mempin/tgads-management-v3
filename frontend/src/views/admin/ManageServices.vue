<script setup lang="ts">
import { Button, DataTable, Column, Tag, useConfirm, useToast, ConfirmDialog } from 'primevue';
import { Plus } from '@lucide/vue';
import { getAllServices, archiveService } from '@/api/services';
import { ref, onMounted } from 'vue';
import type { ServiceType } from '@/types/services';
import { formatCurrency } from '@/utils/formatters';
import ServiceForm from '@/components/ServiceForm.vue';

const confirm = useConfirm();
const toast = useToast();

const servicesList = ref<ServiceType[]>([]);
const fetchServices = async () => {
	servicesList.value = await getAllServices()
	console.log("Fetch successful.")
}
onMounted(async () => {
	fetchServices();
});
const isVisible = ref(false);
const editingData = ref<ServiceType | null>(null)
const openEdit = (data: ServiceType) => {
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
			await archiveService(id)
			await fetchServices();
            toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Service deleted', life: 3000 });
        },
        reject: () => {
            toast.add({ severity: 'error', summary: 'Cancelled', detail: 'You have cancelled', life: 3000 });
        }
    });
}
</script>
<template>
	<ServiceForm v-model:isVisible="isVisible" @saved="fetchServices" :editData="editingData" @update:isVisible="onClose" />
	<ConfirmDialog />
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-lg font-semibold">Manage Services</h1>
			<h2>Configure the services that users can select when creating job orders.</h2>
		</div>
		<Button label="Add Service" @click="isVisible = true">
			<template #icon>
				<Plus />
			</template>
		</Button>
	</section>
	<section class="mt-4 flex-1 h-full rounded-md border border-slate-300 overflow-hidden bg-white">
		<DataTable scrollable scroll-height="flex" :pt="{ root: 'h-full' }" :value="servicesList" dataKey="id"
			tableStyle="min-width: 60rem;" paginator :rows="5" :rowsPerPageOptions="[5, 10, 20, 50]">
			<Column field="name" header="Name"></Column>
			<Column field="abbreviation" header="Abbreviation"></Column>
			<Column field="price" header="Price">
				<template #body="{ data }">
					<p>{{ formatCurrency(data.price) }}</p>
				</template>
			</Column>
			<Column field="unit" header="Unit"></Column>
			<Column header="Area Based">
				<template #body="{ data }">
					<Tag :value="data.is_area_based ? 'Yes' : 'No'"
						:severity="data.is_area_based ? 'success' : 'secondary'" />
				</template>
			</Column>
			<Column field="required_measurement_unit" header="Measurement Unit"></Column>
			<Column style="width: 1rem">
				<template #body="{ data, index }">
					<div class="flex gap-4">
						<Button class="w-20" label="Edit" severity="warn" @click="openEdit(data)" />
						<Button class="w-20" label="Delete" severity="danger" @click="confirmDelete(data.id)"/>
					</div>
				</template>
			</Column>
		</DataTable>
	</section>
</template>