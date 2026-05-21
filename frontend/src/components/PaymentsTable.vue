<script setup lang="ts">
import { DataTable, Column, Button } from 'primevue';
import PaymentsForm from './PaymentsForm.vue';
import { Plus } from '@lucide/vue';
import { ref } from 'vue';
import type { PaymentCreate, Payment, JobItemCreate, JobItem } from '@/types/job_orders';
import { formatDate, formatCurrency } from '@/utils/formatters';

const props = defineProps<{
	payments: PaymentCreate[] | Payment[],
	jobItems: JobItemCreate[] | JobItem[],
	readOnly: boolean
}>()

const isVisible = ref(false);
const editingIndex = ref<number | null>(null)
const editingItem = ref<PaymentCreate | null>(null)

const emit = defineEmits<{
	(e: 'update:payments', value: PaymentCreate[]): void
}>()

const addItem = (newItem: PaymentCreate) => {
	emit('update:payments', [...(props.payments as PaymentCreate[]), newItem])
}
const deleteItem = (index: number) => {
	emit('update:payments', (props.payments as PaymentCreate[]).filter((_, i) => i !== index))
}
const openEdit = (item: PaymentCreate, index: number) => {
	editingItem.value = item
	editingIndex.value = index
	isVisible.value = true
}

const updateItem = (updated: PaymentCreate) => {
	if (editingIndex.value === null) return
	const newPayments = [...(props.payments as PaymentCreate[])]
	newPayments[editingIndex.value] = updated
	emit('update:payments', newPayments)
	editingItem.value = null
	editingIndex.value = null
}
</script>
<template>
	<PaymentsForm v-model:isVisible="isVisible" :editItem="editingItem" @add-item="addItem" @update-item="updateItem" />
	<div class="rounded-md overflow-hidden">
		<DataTable :value="payments">
			<template #empty>
				<p class="text-center text-slate-400">Input data by clicking the + icon on the upper right.</p>
			</template>
			<template #header>
				<div class="flex flex-wrap items-center justify-between gap-2">
					<span class="text-xl font-medium text-slate-600">Payments</span>
					<Button v-if="!readOnly" @click="isVisible = true" severity="contrast" :disabled="!props.jobItems.length"
						v-tooltip.left="{ value: 'Add job items first.', disabled: !!props.jobItems.length }">
						<Plus class="w-4" />
					</Button>
				</div>
			</template>
			<Column header="Date Received" field="date_received">
				<template #body="{ data }">
					<p>{{ formatDate(data.date_received) }}</p>
				</template>
			</Column>
			<Column header="Method" field="method" />
			<Column header="Amount" field="amount">
				<template #body="{ data }">
					<p>{{ formatCurrency(data.amount) }}</p>
				</template>
			</Column>
			<Column style="width: 1rem">
				<template #body="{ data, index }">
					<div class="flex gap-4">
						<Button v-if="!readOnly" class="w-20" label="Edit" severity="warn" @click="openEdit(data, index)" />
						<Button v-if="!readOnly" class="w-20" label="Delete" severity="danger" @click="deleteItem(index)" />
					</div>
				</template>
			</Column>
		</DataTable>
	</div>
</template>