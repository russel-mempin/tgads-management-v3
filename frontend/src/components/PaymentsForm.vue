<script setup lang="ts">
import type { PaymentCreate } from '@/types/job_orders';
import { ref, watch } from 'vue';
import { Dialog, DatePicker, Select, InputNumber, Button } from 'primevue';

const props = defineProps<{
	isVisible: boolean
	editItem?: PaymentCreate | null
}>()

const emit = defineEmits<{
	(e: 'update:isVisible', value: boolean): void
	(e: 'add-item', value: PaymentCreate): void
	(e: 'update-item', value: PaymentCreate): void
}>()

const item = ref<PaymentCreate>({
	date_received: new Date(),
	method: 'Cash',
	amount: 1
})

const paymentMethods = ref(['Cash', 'GCash', 'Cheque'])

const resetItem = () => {
    item.value = {
        date_received: new Date(),
		method: 'Cash',
		amount: 1
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
        item.value = { ...newItem }
    } else {
        resetItem()
    }
})
</script>
<template>
	<Dialog :visible="isVisible" @update:visible="emit('update:isVisible', $event)" modal
		:header="editItem ? 'Edit Payment' : 'Add Payment'" :style="{ width: '40rem' }">
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Date Received</label>
			<DatePicker v-model="item.date_received" showTime hourFormat="12" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Method</label>
			<Select v-model="item.method" :options="paymentMethods" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Amount</label>
			<InputNumber v-model="item.amount" mode="currency" currency="PHP" fluid />
		</div>
		<div class="flex justify-end gap-2">
			<Button label="Cancel" severity="secondary" @click="emit('update:isVisible', false)" />
			<Button label="Save" @click="onSave" />
		</div>
	</Dialog>
</template>