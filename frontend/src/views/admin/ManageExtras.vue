<script setup lang="ts">
import { getAllExtras, archiveExtraService } from '@/api/services';
import { ref, onMounted } from 'vue'
import type { ExtraService } from '@/types/services';
import { Button, DataTable, Column, useConfirm, useToast, ConfirmDialog } from 'primevue';
import { Plus, Info } from '@lucide/vue';
import { formatCurrency } from '@/utils/formatters';
import ExtraForm from '@/components/ExtraForm.vue';

const confirm = useConfirm();
const toast = useToast();
const extrasList = ref<ExtraService[]>([]);
const fetchExtras = async () => {
	extrasList.value = await getAllExtras()
	console.log(extrasList.value)
}
onMounted(async () => {
	fetchExtras()
});
const isVisible = ref(false);
const editingData = ref<ExtraService | null>(null)

const openEdit = (data: ExtraService) => {
    editingData.value = data
    isVisible.value = true
}
const onClose = () => {
    editingData.value = null
    isVisible.value = false
}
const confirmDelete = (id: string) => {
	confirm.require({
        message: 'Do you want to delete this extra?',
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
			await archiveExtraService(id)
			await fetchExtras();
            toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Extra deleted', life: 3000 });
        },
        reject: () => {
            toast.add({ severity: 'error', summary: 'Cancelled', detail: 'You have cancelled', life: 3000 });
        }
    });
}
</script>

<template>
	<ExtraForm v-model:isVisible="isVisible" @saved="fetchExtras" :editData="editingData" @update:isVisible="onClose" />
	<ConfirmDialog>
		<template #icon>
			<Info class="w-10 h-10 text-red-500" />
		</template>
	</ConfirmDialog>
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-lg font-semibold">Manage Extras</h1>
			<h2>Configure the extra services that users can select when creating job orders.</h2>
		</div>
		<Button label="Add Extra" @click="isVisible = true">
			<template #icon>
				<Plus />
			</template>
		</Button>
	</section>
	<section class="mt-4 flex-1 h-full rounded-md border border-slate-300 overflow-hidden bg-white">
		<DataTable scrollable scroll-height="flex" :pt="{ root: 'h-full' }" :value="extrasList" dataKey="id"
			tableStyle="min-width: 60rem;" paginator :rows="5" :rowsPerPageOptions="[5, 10, 20, 50]">
			<Column field="name" header="Name"></Column>
			<Column field="price" header="Price">
				<template #body="{ data }">
					<p>{{ formatCurrency(data.price) }}</p>
				</template>
			</Column>
			<Column style="width: 1rem">
				<template #body="{ data }">
					<div class="flex gap-4">
						<Button class="w-20" label="Edit" severity="warn" @click="openEdit(data)" />
						<Button class="w-20" label="Delete" severity="danger" @click="confirmDelete(data.id)"/>
					</div>
				</template>
			</Column>
		</DataTable>
	</section>
</template>