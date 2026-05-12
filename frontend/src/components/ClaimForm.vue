<script setup lang="ts">
import type { ClaimCreate, JobItemCreate } from '@/types/job_orders';
import { ref, watch, computed } from 'vue';
import { Dialog, DatePicker, InputText, Select, InputNumber, Button } from 'primevue';

const props = defineProps<{
	isVisible: boolean
	editItem?: ClaimCreate | null
	jobItems: JobItemCreate[]
	claims: ClaimCreate[]
}>()

const emit = defineEmits<{
	(e: 'update:isVisible', value: boolean): void
	(e: 'add-item', value: ClaimCreate): void
	(e: 'update-item', value: ClaimCreate): void
}>()

const item = ref<ClaimCreate>({
	date_claimed: new Date(),
	name: '',
	job_item_id: '',
	pcs_claimed: 1,
})

const resetItem = () => {
	item.value = {
		date_claimed: new Date(),
		name: '',
		job_item_id: '',
		pcs_claimed: 1,
	}
}

const maxClaimable = computed(() => {
	if (!item.value.job_item_id) return 0

	const jobItem = props.jobItems.find(i => i.item_id === item.value.job_item_id)
	if (!jobItem) return 0

	const alreadyClaimed = props.claims
		.filter(c => c.job_item_id === item.value.job_item_id)
		.filter((_, i) => !props.editItem || props.claims.indexOf(props.editItem) !== i)
		.reduce((sum, c) => sum + c.pcs_claimed, 0)
		
	return jobItem.quantity - alreadyClaimed
})

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
		:header="editItem ? 'Edit Claim History' : 'Add Claim History'" :style="{ width: '40rem' }">
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Date Claimed</label>
			<DatePicker v-model="item.date_claimed" showTime hourFormat="12" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Name</label>
			<InputText v-model="item.name" fluid autocomplete="off" />
		</div>
		<div class="grid grid-cols-2 gap-4 mb-4">
			<div class="flex flex-col">
				<label class="font-semibold mb-1">Item Claimed</label>
				<Select v-model="item.job_item_id" :options="props.jobItems.map(i => i.item_id)" fluid />
			</div>
			<div class="flex flex-col">
				<label class="font-semibold mb-1">Pcs. Claimed</label>
				<InputNumber v-model="item.pcs_claimed" :min="1" :max="maxClaimable" fluid />
			</div>
		</div>
		<div class="flex justify-end gap-2">
			<Button label="Cancel" severity="secondary" @click="emit('update:isVisible', false)" />
			<Button label="Save" @click="onSave" />
		</div>
	</Dialog>
</template>