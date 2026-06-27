<script setup lang="ts">
import type { Expense } from '@/types/expenses';
import { ref, watch } from 'vue';
import { Dialog, DatePicker, Select, InputNumber, InputText, Button, useToast } from 'primevue';
import { nowInManila } from '@/utils/formatters';
import { createExpense, updateExpense } from '@/api/expenses';

const toast = useToast();
const props = defineProps<{
	isVisible: boolean
	editItem?: Expense | null
}>()

const emit = defineEmits<{
	(e: 'update:isVisible', value: boolean): void
	(e: 'saved'): void
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

const onSave = async () => {
	try {
		if (props.editItem) {
			if (!props.editItem.id) {
				toast.add({ severity: 'error', summary: 'Error', detail: 'Missing expense ID.', life: 3000 })
				return
			}
			await updateExpense(props.editItem.id, item.value)
		} else {
			await createExpense(item.value)
		}
		toast.add({ severity: 'success', summary: 'Saved', detail: 'Data saved successfully.', life: 3000 })
		emit('saved')
		emit('update:isVisible', false)
		resetItem()
	} catch (error: any) {
		toast.add({ severity: 'error', summary: 'Error', detail: error.response?.data?.detail ?? 'Failed to save data.', life: 3000 })
		console.error(error.response?.data || error)
	}
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
		<p class="text-gray-500 font-medium mb-4">Fields marked with<span class="text-red-500 font-semiold"> *
			</span>are
			required.</p>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Date<span class="text-red-500 font-semibold"> *</span></label>
			<DatePicker v-model="item.date" showTime hourFormat="12" dateFormat="M dd, yy" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Category<span class="text-red-500 font-semibold"> *</span></label>
			<Select v-model="item.category" :options="expenseCategories" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Amount<span class="text-red-500 font-semibold"> *</span></label>
			<InputNumber v-model="item.amount" mode="currency" currency="PHP" fluid :minFractionDigits="0"
				:maxFractionDigits="2" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Description<span class="text-red-500 font-semibold"> *</span></label>
			<InputText v-model="item.description" fluid autocomplete="off" />
		</div>
		<div class="flex justify-end gap-2">
			<Button class="w-24" label="Cancel" severity="secondary" @click="emit('update:isVisible', false)" />
			<Button class="w-24" label="Save" @click="onSave" />
		</div>
	</Dialog>
</template>