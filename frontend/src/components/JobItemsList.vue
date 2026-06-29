<script setup lang="ts">
// JobItemsList.vue
import type { JobItem } from '@/types/job_orders';
import { Button, Tag } from 'primevue'
import { Plus } from '@lucide/vue';
import { formatDate, formatCurrency, formatNullable, mapCustomColor, mapSeverity } from '@/utils/formatters';
import { ref } from 'vue';
import JobItemsForm from './JobItemsForm.vue';

const props = defineProps<{
	items: JobItem[] | JobItem[],
	jo_number: number,
	readOnly: boolean
}>()

const isVisible = ref(false);

const emit = defineEmits<{
	(e: 'update:items', value: JobItem[]): void
}>()

const addItem = (newItem: JobItem) => {
	emit('update:items', [...(props.items as JobItem[]), newItem])
}

const deleteItem = (itemId: string) => {
	emit('update:items', (props.items as JobItem[]).filter(i => i.item_id !== itemId))
}

const editingItem = ref<JobItem | null>(null)

const openEdit = (value: JobItem) => {
	editingItem.value = {
		...value,
		due_date: new Date(value.due_date),
	}
	isVisible.value = true
}

const updateItem = (updated: JobItem) => {
	emit('update:items', (props.items as JobItem[]).map(i =>
		i.item_id === updated.item_id ? updated : i
	))
	editingItem.value = null
}
</script>
<template>
	<JobItemsForm v-if="!readOnly" v-model:isVisible="isVisible" :joNumber="jo_number"
		:existingItems="(items as JobItem[])" :editItem="editingItem" @add-item="addItem" @update-item="updateItem" />
	<div class="bg-white rounded-2xl border border-gray-200 shadow-xs">
		<div class="px-6 py-3 flex items-center justify-between border-b border-slate-200">
			<p class="text-xl font-medium text-slate-600">Job Items</p>
			<Button variant="outlined" label="Add Item" iconPos="left" v-if="!readOnly" @click="isVisible = true"
				severity="contrast" :disabled="!props.jo_number"
				v-tooltip.left="{ value: 'Please enter JO Number first.', disabled: !!props.jo_number }">
				<template #icon>
					<Plus class="w-4" />
				</template>
			</Button>
		</div>
		<div v-if="!props.items.length" class="flex flex-col items-center gap-4 p-4">
			<p class="text-center text-slate-400">No items yet — add the first one to start
				this job.
			</p>
			<Button label="Add Item" iconPos="left" v-if="!readOnly" @click="isVisible = true" severity="primary"
				:disabled="!props.jo_number"
				v-tooltip.left="{ value: 'Please enter JO Number first.', disabled: !!props.jo_number }">
				<template #icon>
					<Plus class="w-4" />
				</template>
			</Button>
		</div>
		<div class="overflow-y-auto max-h-121">
			<div v-for="value in props.items" class="p-4">
				<div class="border border-slate-300 rounded-md">
					<div
						class="bg-slate-100 rounded-tl-md rounded-tr-md flex justify-between border-b border-slate-300">
						<span class="p-4 grid grid-cols-2 items-center gap-10">
							<p class="font-medium text-slate-700">{{ value.item_id }}</p>
							<p class="text-slate-800">{{ value.service_name }}</p>
						</span>
						<span class="p-4 flex items-center gap-4">
							<Tag :value="value.job_status"
								:severity="mapCustomColor(value.job_status) ? undefined : mapSeverity(value.job_status)"
								:class="mapCustomColor(value.job_status)" 
							/>
							<p class="text-slate-700">Due {{ formatDate(value.due_date.toString()) }}</p>
							<p class="font-semibold text-lg text-slate-800 text-right">{{
								formatCurrency(((value.unit_price ?? 0) +
									(value.extra_service_price ?? 0) - value.discount) * value.quantity) }}</p>
						</span>
					</div>
					<div class="p-4 flex gap-4">
						<div class="flex-auto">
							<p class="text-xs font-medium text-slate-500">DIMENSIONS</p>
							<p class="text-slate-800">{{ value.height }}{{ value.size_unit }} × {{ value.width }}{{
								value.size_unit }}</p>
						</div>
						<div class="flex-auto">
							<p class="text-xs font-medium text-slate-500">UNIT PRICE</p>
							<p class="font-medium text-slate-800">{{ formatCurrency(value.unit_price) }}</p>
						</div>
						<div class="flex-auto">
							<p class="text-xs font-medium text-slate-500">QUANTITY</p>
							<p class="font-medium text-slate-800">{{ value.quantity }}</p>
						</div>
						<div class="flex-auto">
							<p class="text-xs font-medium text-slate-500">EXTRA</p>
							<p class="text-slate-800">{{ value.extra_service_name }} / {{
								formatCurrency(value.extra_service_price) }}</p>
						</div>
						<div class="flex-auto">
							<p class="text-xs font-medium text-slate-500">DISCOUNT</p>
							<p class="text-slate-800">- {{ formatCurrency(value.discount) }}</p>
						</div>
					</div>
					<div class="p-4 flex gap-4">
						<div class="flex-auto">
							<p class="text-xs font-medium text-slate-500">DESCRIPTION</p>
							<p class="text-slate-800">{{ formatNullable(value.description) }}</p>
						</div>
						<div class="flex-auto">
							<p class="text-xs font-medium text-slate-500">NOTES</p>
							<p class="text-slate-800">{{ formatNullable(value.notes) }}</p>
						</div>
						<div class="flex gap-4">
							<Button v-if="!readOnly" severity="warn" class="w-20"
								@click="openEdit(value as JobItem)">Edit</Button>
							<Button v-if="!readOnly" severity="danger" class="w-20"
								@click="deleteItem(value.item_id)">Delete</Button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>