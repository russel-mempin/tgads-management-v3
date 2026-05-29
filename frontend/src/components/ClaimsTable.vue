<script setup lang="ts">
import { DataTable, Column, Button } from 'primevue';
import ClaimForm from './ClaimForm.vue';
import { Plus } from '@lucide/vue';
import { ref } from 'vue';
import type { ClaimCreate, ClaimingHistory, JobItemCreate, JobItem } from '@/types/job_orders';
import { formatDate } from '@/utils/formatters';

const props = defineProps<{
    claims: ClaimCreate[] | ClaimingHistory[],
    jobItems: JobItemCreate[] | JobItem[],
    readOnly?: boolean
}>()

const isVisible = ref(false);
const editingIndex = ref<number | null>(null)
const editingItem = ref<ClaimCreate | null>(null)

const emit = defineEmits<{
	(e: 'update:claims', value: ClaimCreate[]): void
}>()

const addItem = (newItem: ClaimCreate) => {
	emit('update:claims', [...(props.claims as ClaimCreate[]), newItem])
}
const deleteItem = (index: number) => {
	emit('update:claims', (props.claims as ClaimCreate[]).filter((_, i) => i !== index))
}
const openEdit = (item: ClaimCreate, index: number) => {
	editingItem.value = item
	editingIndex.value = index
	isVisible.value = true
}

const updateItem = (updated: ClaimCreate) => {
	if (editingIndex.value === null) return
	const newClaims = [...(props.claims as ClaimCreate[])]
	newClaims[editingIndex.value] = updated
	emit('update:claims', newClaims)
	editingItem.value = null
	editingIndex.value = null
}
</script>
<template>
	<ClaimForm v-model:isVisible="isVisible" :editItem="editingItem" :jobItems="props.jobItems" :claims="props.claims"
		@add-item="addItem" @update-item="updateItem" />
	<div class="rounded-md overflow-hidden">
		<DataTable :value="claims">
			<template #empty>
				<p class="text-center text-slate-400">Input data by clicking the + icon on the upper right.</p>
			</template>
			<template #header>
				<div class="flex flex-wrap items-center justify-between gap-2">
					<span class="text-xl font-medium text-slate-600">Claiming History</span>
					<Button v-if="!readOnly" @click="isVisible = true" severity="contrast" :disabled="!props.jobItems.length"
						v-tooltip.left="{ value: 'Add job items first.', disabled: !!props.jobItems.length }">
						<Plus class="w-4" />
					</Button>
				</div>
			</template>
			<Column header="Date Claimed" field="date_claimed">
				<template #body="{ data }">
					<p>{{ formatDate(data.date_claimed) }}</p>
				</template>
			</Column>
			<Column header="Name" field="name" />
			<Column header="Item Claimed" field="claimed_item_id" />
			<Column header="Pcs." field="pcs_claimed">
				<template #body="{ data }">
					<p>{{ data.pcs_claimed }} pc(s).</p>
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