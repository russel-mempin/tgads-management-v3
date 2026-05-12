<script setup lang="ts">
// JobItemsList.vue
import type { JobItemCreate } from '@/types/job_orders';
import { Button, Tag } from 'primevue'
import { Plus } from '@lucide/vue';
import { formatDate, formatCurrency } from '@/utils/formatters';
import { ref } from 'vue';
import JobItemsForm from './JobItemsForm.vue';

const props = defineProps<{
	items: JobItemCreate[],
	jo_number: number,
}>()

const isVisible = ref(false);

const emit = defineEmits<{
	(e: 'update:items', value: JobItemCreate[]): void
}>()

const addItem = (newItem: JobItemCreate) => {
	emit('update:items', [...props.items, newItem])
}
const deleteItem = (itemId: string) => {
	emit('update:items', props.items.filter(i => i.item_id !== itemId))
}

const editingItem = ref<JobItemCreate | null>(null)

const openEdit = (value: JobItemCreate) => {
	editingItem.value = value
	isVisible.value = true
}

const updateItem = (updated: JobItemCreate) => {
	emit('update:items', props.items.map(i =>
		i.item_id === updated.item_id ? updated : i
	))
	editingItem.value = null
}
</script>
<template>
	<JobItemsForm v-model:isVisible="isVisible" :joNumber="jo_number" :existingItems="items" :editItem="editingItem"
		@add-item="addItem" @update-item="updateItem" />
	<div class="bg-white rounded-md">
		<div class="px-4 py-3 flex items-center justify-between border-b border-slate-200">
			<p class="text-xl font-medium text-slate-600">Job Items</p>
			<Button @click="isVisible = true" severity="contrast" :disabled="!props.jo_number"
				v-tooltip.left="{ value: 'Please enter JO Number first.', disabled: !!props.jo_number }">
				<Plus class="w-4" />
			</Button>
		</div>
		<p v-if="!props.items.length" class="text-center p-4 text-slate-400">Input data by clicking the + icon on the
			upper right.</p>
		<div class="overflow-y-auto max-h-121">
			<div v-for="value in props.items" class="p-4">
				<div class="border border-slate-300 rounded-md">
					<div
						class="bg-slate-100 rounded-tl-md rounded-tr-md flex justify-between border-b border-slate-300">
						<span class="p-4 grid grid-cols-2 items-center gap-10">
							<p class="font-medium text-slate-700">{{ value.item_id }}</p>
							<p class="text-slate-800">{{ value.service_name }}</p>
						</span>
						<span class="p-4 grid grid-cols-3 items-center gap-4">
							<Tag :value="value.job_status" rounded />
							<p class="text-slate-700">Due {{ formatDate(value.due_date.toString()) }}</p>
							<p class="font-semibold text-lg text-slate-800 text-right">{{
								formatCurrency((value.unit_price +
									value.extra_service_price - value.discount) * value.quantity) }}</p>
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
							<p class="text-xs font-medium text-slate-500">PAPER SIZE</p>
							<p class="text-slate-800">{{ value.paper_size }}</p>
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
							<p class="text-slate-800">{{ value.description ? value.description : '-' }}</p>
						</div>
						<div class="flex-auto">
							<p class="text-xs font-medium text-slate-500">NOTES</p>
							<p class="text-slate-800">{{ value.notes ? value.notes : '-' }}</p>
						</div>
						<div class="flex gap-4">
							<Button severity="warn" class="w-20" @click="openEdit(value)">Edit</Button>
							<Button severity="danger" class="w-20" @click="deleteItem(value.item_id)">Delete</Button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>