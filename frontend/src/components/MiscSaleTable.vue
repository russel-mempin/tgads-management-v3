<script setup lang="ts">
import type { MiscSale } from '@/types/miscSale';
import type { TableColumn } from '@nuxt/ui';
import { formatDate, formatCurrency } from '@/utils/formatters';

const props = defineProps<{
    miscSale: MiscSale[]
}>()

const columns: TableColumn<MiscSale>[] = [
	{
		accessorKey: 'reference_number',
		header: 'Reference No.',
		cell: ({ row }) => row.getValue('reference_number') || '—',
	},
	{
		accessorKey: 'date',
		header: 'Date',
		cell: ({ row }) => `${formatDate(row.getValue('date'))}`
	},
	{
		accessorKey: 'description',
		header: 'Description',
	},
	{
		accessorKey: 'amount',
		header: 'Amount',
		cell: ({ row }) => `${formatCurrency(row.getValue('amount'))}`
	},
	{
		accessorKey: 'account_name',
		header: 'Method',
	},
	{
		accessorKey: 'created_by_name',
		header: 'Added By',
	},
	{
		accessorKey: 'updated_by_name',
		header: 'Last Updated By',
		cell: ({ row }) => row.getValue('updated_by_name') || '—',
	},
	{
		id: 'actions',
		header: ''
	}
]
</script>

<template>
    <UTable :data="miscSale" :columns="columns" sticky class="overflow-y-auto h-full">
        <template #actions-cell="{ row }">
            <slot name="actions" :item="row.original" :index="row.index" />
        </template>
    </UTable>
</template>