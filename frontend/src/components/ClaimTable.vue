<script setup lang="ts">
import type { JobItemTableRow, ClaimingHistory } from '@/types/jobOrder';
import type { TableColumn } from '@nuxt/ui';
import { formatDate } from '@/utils/formatters.ts';

const props = defineProps<{
	jobItems: JobItemTableRow[]
	claimingHistory: ClaimingHistory[]
	claimableItems: string[]
	isJobCancelled?: boolean
}>()

const emit = defineEmits<{
	openForm: []
}>()

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
		header: ''
	}
]
</script>

<template>
	<section class="bg-default border border-default rounded-md">
		<div class="rounded-tl-md rounded-tr-md flex items-center justify-between p-4 border-b border-default">
			<div class="flex items-center gap-2">
				<UIcon name="i-lucide-scroll-text" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
				<h2 class="text-highlighted font-semibold">Claiming History</h2>
			</div>
			<UTooltip :text="(jobItems.length <= 0 || claimableItems.length <= 0 || isJobCancelled) ? 'No available items to claim.' : 'Log payment record.'">
				<span>
					<UButton @click="emit('openForm')" :disabled="jobItems.length <= 0 || claimableItems.length <= 0 || isJobCancelled" icon="i-lucide-plus"
						label="Add Item" variant="outline" />
				</span>
			</UTooltip>
		</div>
		<UTable :data="claimingHistory" :columns="columns">
			<template #actions-cell="{ row }">
				<slot name="actions" :item="row.original" :index="row.index" />
			</template>
			<template #empty>
				<div class="text-sm text-muted text-center">
					No claim history recorded yet.
				</div>
			</template>
		</UTable>
	</section>
</template>