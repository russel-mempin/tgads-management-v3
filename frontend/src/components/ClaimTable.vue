<script setup lang="ts">
import { ref, h, resolveComponent } from 'vue'
import type { JobItemCreate, ClaimingHistory } from '@/types/jobOrder';
import ClaimForm from './ClaimForm.vue';
import type { TableColumn } from '@nuxt/ui';
import { formatDate } from '@/utils/formatters.ts';

const props = defineProps<{
	jobItems: JobItemCreate[]
	claimingHistory: ClaimingHistory[]
}>()

const emit = defineEmits<{
	addClaim: [claim: ClaimingHistory]
	removeClaim: [index: number]
	updateClaim: [claim: ClaimingHistory, index: number]
}>()

// UI Variables
const isOpen = ref(false)
const isDeleteConfirmOpen = ref(false)
const UButton = resolveComponent('UButton')

// Data Variables
const itemPendingDelete = ref<ClaimingHistory | null>(null)
const itemPendingDeleteIndex = ref<number | null>(null)
const itemPendingEdit = ref<ClaimingHistory | null>(null)
const itemPendingEditIndex = ref<number | null>(null)

// UI Functions
const openAddForm = () => {
	itemPendingEdit.value = null
	itemPendingEditIndex.value = null
	isOpen.value = true
}
const requestRemoveClaim = (item: ClaimingHistory, index: number) => {
	itemPendingDelete.value = item
	itemPendingDeleteIndex.value = index
	isDeleteConfirmOpen.value = true
}
const cancelRemoveClaim = () => {
	isDeleteConfirmOpen.value = false
	itemPendingDelete.value = null
}
const confirmRemoveClaim = () => {
    if (itemPendingDeleteIndex.value === null) return
    emit('removeClaim', itemPendingDeleteIndex.value)
    isDeleteConfirmOpen.value = false
    itemPendingDelete.value = null
    itemPendingDeleteIndex.value = null
}

const requestEditClaim = (claim: ClaimingHistory, index: number) => {
	itemPendingEdit.value = claim
	itemPendingEditIndex.value = index
	isOpen.value = true
}


// Data Functions
const handleSave = (claim: ClaimingHistory) => {
	if (itemPendingEditIndex.value !== null) {
		emit('updateClaim', claim, itemPendingEditIndex.value)
	} else {
		emit('addClaim', claim)
	}
	itemPendingEdit.value = null
	itemPendingEditIndex.value = null
}

// Table Display
const columns: TableColumn<ClaimingHistory>[] = [
	{ accessorKey: 'claimed_item_id', header: 'Claimed ID' },
	{
		accessorKey: 'pcs_claimed',
		header: 'Pieces Claimed',
		cell: ({ row }) => `${row.original.pcs_claimed} pc(s)`
	},
	{
		accessorKey: 'date_claimed',
		header: 'Date Received',
		cell: ({ row }) => `${formatDate(row.original.date_claimed)}`
	},
	{ accessorKey: 'name', header: 'Name' },
	{
		id: 'actions',
		header: 'Actions',
		cell: ({ row }) =>
			h('div', { class: 'flex items-center gap-2' }, [
				h(UButton, {
					color: 'warning',
					variant: 'ghost',
					icon: 'i-lucide-square-pen',
					size: 'md',
					onClick: (e: Event) => {
						e.stopPropagation()
						requestEditClaim(row.original, row.index)
					}
				}),
				h(UButton, {
					icon: 'i-lucide-trash-2',
					color: 'error',
					variant: 'ghost',
					size: 'md',
					onClick: (e: Event) => {
						e.stopPropagation()
						requestRemoveClaim(row.original, row.index)
					},
				}),
			])
	}
]
</script>

<template>
	<UModal v-model:open="isDeleteConfirmOpen" title="Delete Claim?">
		<template #body>
			<p class="text-sm text-muted">
				Are you sure you want to delete claim for job item
				<span class="font-semibold text-highlighted">{{ itemPendingDelete?.claimed_item_id }}</span>? This can't
				be undone.
			</p>
			<div class="flex justify-end gap-3 mt-6">
				<UButton label="Cancel" color="neutral" variant="outline" @click="cancelRemoveClaim" />
				<UButton label="Delete" color="error" @click="confirmRemoveClaim" />
			</div>
		</template>
	</UModal>
	<ClaimForm v-model:isOpen="isOpen" :jobItems="jobItems" :editing-claim="itemPendingEdit" @save="handleSave" />
	<div class="bg-default border border-default rounded-md p-6 m-8">
		<div class="flex justify-between items-center gap-2 mb-6">
			<div class="flex items-center gap-2">
				<UIcon name="i-lucide-scroll-text" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
				<p class="font-semibold text-highlighted">Claiming History</p>
			</div>
			<UTooltip text="Input a job item first.">
				<UButton @click="openAddForm" label="Add Claim" :disabled="!jobItems.length" icon="i-lucide-plus" />
			</UTooltip>
		</div>
		<!-- Empty state -->
		<div v-if="!props.claimingHistory.length" class="text-sm text-muted text-center">
			No claims recorded yet.
		</div>
		<UTable v-else :data="claimingHistory" :columns="columns" class="border border-default rounded-md" />
	</div>
</template>