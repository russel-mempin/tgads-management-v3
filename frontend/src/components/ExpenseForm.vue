<script setup lang="ts">
import type { Expense } from '@/types/expenses';
import { ref, watch } from 'vue';
import { Dialog, DatePicker, Select, InputNumber, InputText, Button } from 'primevue';
import { nowInManila } from '@/utils/formatters';

const props = defineProps<{
	isVisible: boolean
	editItem?: Expense | null
}>()

const emit = defineEmits<{
	(e: 'update:isVisible', value: boolean): void
	(e: 'add-item', value: Expense): void
	(e: 'update-item', value: Expense): void
}>()

const item = ref<Expense>({
	date: nowInManila(),
	category: 'Food',
	amount: 1,
	description: '',
})
const expenseCategories = ref(['Food', 'Maintenance', 'Utilities', 'Transportation', 'Supplies', 'Payroll', 'Benefits', 'Production', 'Miscellaneous'])

const resetItem = () => {
	item.value = {
		date: nowInManila(),
		category: 'Food',
		amount: 1,
		description: '',
	}
}

const onSave = () => {
	if (props.editItem) {
		emit('update-item', { ...item.value })
	} else {
		console.log("Hi")
		emit('add-item', { ...item.value })
	}
	emit('update:isVisible', false)
	resetItem()
}

watch(() => props.editItem, (newItem) => {
	if (newItem) {
		item.value = { ...newItem, date: new Date(newItem.date) }
	} else {
		resetItem()
	}
})
</script>
<template>
	<Dialog :visible="isVisible" @update:visible="emit('update:isVisible', $event)" modal
		:header="editItem ? 'Edit Expense' : 'Add Expense'" :style="{ width: '40rem' }">
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Date</label>
			<DatePicker v-model="item.date" showTime hourFormat="12" dateFormat="M dd, yy" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Category</label>
			<Select v-model="item.category" :options="expenseCategories" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Amount</label>
			<InputNumber v-model="item.amount" mode="currency" currency="PHP" fluid :minFractionDigits="0"
				:maxFractionDigits="2" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Description</label>
			<InputText v-model="item.description" fluid autocomplete="off" />
		</div>
		<div class="flex justify-end gap-2">
			<Button class="w-24" label="Cancel" severity="secondary" @click="emit('update:isVisible', false)" />
			<Button class="w-24" label="Save" @click="onSave" />
		</div>
	</Dialog>
</template>