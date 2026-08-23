<script setup lang="ts">
import type { Payment } from '@/types/jobOrder';
import type { TableColumn } from '@nuxt/ui';
import { formatDate, formatCurrency } from '@/utils/formatters';

const props = defineProps<{
	balance: number
	payments: Payment[]
	isJobCancelled?: boolean
}>()
const emit = defineEmits<{
	openForm: []
}>()

// Table data
const columns: TableColumn<Payment>[] = [
	{
		accessorKey: 'date_received',
		header: 'Date Received',
		cell: ({ row }) => `${formatDate(row.original.date_received)}`
	},
	{ accessorKey: 'reference_number', header: 'Reference No.' },
	{
		accessorKey: 'amount',
		header: 'Amount',
		cell: ({ row }) => `${formatCurrency(row.original.amount)}`
	},
	{ accessorKey: 'account_name_snapshot', header: 'Method' },
	{ accessorKey: 'notes', header: 'Notes', cell: ({ row }) => row.original.notes || '—', },
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
				<UIcon name="i-lucide-philippine-peso"
					class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
				<h2 class="text-highlighted font-semibold">Payments</h2>
			</div>
			<UTooltip :text="(balance <= 0 || isJobCancelled)? 'Customer has no balance.' : 'Log payment record.'">
				<span>
					<UButton @click="emit('openForm')" :disabled="balance <= 0 || isJobCancelled" icon="i-lucide-plus" label="Add Item"
						variant="outline" />
				</span>
			</UTooltip>
		</div>
		<UTable :data="props.payments" :columns="columns">
			<template #actions-cell="{ row }">
				<slot name="actions" :item="row.original" :index="row.index" />
			</template>
			<template #empty>
				<div class="text-sm text-muted text-center">
					No payments recorded yet.
				</div>
			</template>
		</UTable>
	</section>
</template>