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
		id: 'actions',
		header: ''
	}
]
</script>

<template>
    <UTable :data="miscSale" :columns="columns">
        <template #actions-cell="{ row }">
            <slot name="actions" :item="row.original" :index="row.index" />
        </template>
    </UTable>
</template>