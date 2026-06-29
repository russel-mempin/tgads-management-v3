<script setup lang="ts">
// JobItemsTable.vue
import { onMounted, computed, ref } from 'vue';
import { getAllServices, getAllExtras } from '@/api/services';
import type { JobItem } from '@/types/job_orders';
import type { ServiceType } from '@/types/services';
import { Button, DataTable, Column, Tag } from 'primevue';
import { Plus, Trash, SquarePen } from '@lucide/vue'
import { formatCurrency, formatDate } from '@/utils/formatters';
import JobItemsForm from './JobItemsForm.vue';


const serviceList = ref<ServiceType[]>([]);
const extraList = ref<{ id: string, name: string, price: number }[]>([]);
onMounted(async () => {
	serviceList.value = await getAllServices()
	extraList.value = await getAllExtras()
});

const props = defineProps<{
	items: JobItem[],
	jo_number: number,
}>()
const isVisible = ref(false);

const emit = defineEmits<{
	(e: 'update:items', value: JobItem[]): void
}>()

const localItems = computed({
	get: () => props.items,
	set: (value) => emit('update:items', value)
})

const addItem = (newItem: JobItem) => {
	localItems.value = [...localItems.value, newItem]
}
</script>

<template>
	<JobItemsForm v-model:isVisible="isVisible" :joNumber="jo_number" :existingItems="localItems" @add-item="addItem" />
	<DataTable :value="localItems" scrollable>
		<template #empty>
			<p class="text-slate-400">Please input the data required above first.</p>
		</template>
		<template #header>
			<div class="flex flex-wrap items-center justify-between gap-2">
				<span class="text-xl font-medium text-slate-600">Job Items</span>
				<Button @click="isVisible = true" severity="contrast" :disabled="!props.jo_number">
					<Plus class="w-4" />
				</Button>
			</div>
		</template>
		<Column header="ID" field="item_id" style="min-width: 175px" />
		<Column header="Type" field="service_name" style="min-width: 175px" />
		<Column header="Unit" field="size_unit" />
		<Column header="Height" field="height" />
		<Column header="Width" field="width" />
		<Column header="Price">
			<template #body="{ data }">
				{{ formatCurrency(data.unit_price) }}
			</template>
		</Column>
		<Column header="Quantity" field="quantity" />

		<Column header="Extra Type" field="extra_service_name" style="min-width: 150px" />
		<Column header="Extra Price" style="min-width: 120px">
			<template #body="{ data }">
				{{ formatCurrency(data.extra_service_price) }}
			</template>
		</Column>
		<Column header="Discount" field="discount">
			<template #body="{ data }">
				{{ formatCurrency(data.discount) }}
			</template>
		</Column>
		<Column header="Subtotal">
			<template #body="{ data }">
				{{ formatCurrency((data.unit_price + data.extra_service_price - data.discount) * data.quantity) }}
			</template>
		</Column>
		<Column header="Description" field="description" style="min-width: 150px" />
		<Column header="Job Status" field="job_status" style="min-width: 150px">
			<template #body="{ data }">
				<Tag :value="data.job_status" />
			</template>
		</Column>
		<Column header="Due" field="due_date" style="min-width: 150px">
			<template #body="{ data }">
				{{ formatDate(data.due_date) }}
			</template>
		</Column>
		<Column>
			<template #body="{ index }">
				<div class="flex gap-2">
					<Button severity="warn">
						<SquarePen class="w-4" />
					</Button>
					<Button severity="danger">
						<Trash class="w-4" />
					</Button>
				</div>
			</template>
		</Column>
	</DataTable>
</template>