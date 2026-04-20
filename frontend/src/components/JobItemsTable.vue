<script setup lang="ts">
import { computed, watch } from 'vue';
import type { JobItem } from '@/types/job_orders';
import type { ServiceType } from '@/types/services';
import { Button, Select, InputText, DataTable, Column, InputNumber } from 'primevue';
import { Plus, Trash } from '@lucide/vue'

const props = defineProps<{
	items: JobItem[],
	jo_number: number,
	service_list: ServiceType[]
}>()

const emit = defineEmits<{
	(e: 'update:items', value: JobItem[]): void
}>()

const localItems = computed({
	get: () => props.items,
	set: (value) => emit('update:items', value)
})

const onServiceChange = (service: ServiceType, row: JobItem) => {
	row.service_name = service.name
	row.size_unit = service.required_measurement_unit
}
</script>

<template>
	<DataTable :value="localItems" scrollable>
		<template #header>
			<div class="flex flex-wrap items-center justify-between gap-2">
				<span class="text-xl font-medium text-slate-600">Job Items</span>
				<Button severity="contrast">
					<Plus />
				</Button>
			</div>
		</template>
		<Column field="item_id" header="Item ID" />
		<Column header="Type">
			<template #body="{ data }">
				<Select :modelValue="service_list.find(s => s.name === data.service_name)" :options="service_list"
					optionLabel="name" placeholder="Service Type" @change="(e) => onServiceChange(e.value, data)" />
			</template>
		</Column>
		<Column header="Height">
			<template #body="{ data }">
				<InputNumber v-model="data.height" placeholder="Height" />
			</template>
		</Column>
		<Column header="Width">
			<template #body="{ data }">
				<InputNumber v-model="data.width" placeholder="Width" />
			</template>
		</Column>
		<Column header="Unit" field="size_unit"/>
		<Column header="Unit Price">
			<template #body="{ data }">
				<p>{{ data.unit_price }}</p>
			</template>
		</Column>
	</DataTable>
</template>