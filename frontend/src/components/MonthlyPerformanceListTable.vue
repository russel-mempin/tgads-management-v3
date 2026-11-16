<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui';
import { formatDate, formatCurrency } from '@/utils/formatters';
import type { MonthlyPerformanceBase } from '@/types/performance';

const props = defineProps<{
    data: MonthlyPerformanceBase[]
}>()

const columns: TableColumn<MonthlyPerformanceBase>[] = [
    {
        accessorKey: 'month',
        header: 'Month',
    },
    {
        accessorKey: 'collected',
        header: 'Collected',
		cell: ({ row }) => `${formatCurrency(row.getValue('collected'))}`
    },
    {
        accessorKey: 'expenses',
        header: 'Expenses',
		cell: ({ row }) => `${formatCurrency(row.getValue('expenses'))}`

    },
    {
        accessorKey: 'net',
        header: 'Net',
		cell: ({ row }) => `${formatCurrency(row.getValue('net'))}`

    },
    {
        accessorKey: 'sales',
        header: 'Sales',
		cell: ({ row }) => `${formatCurrency(row.getValue('sales'))}`

    },
    {
        accessorKey: 'receivables',
        header: 'Receivables',
		cell: ({ row }) => `${formatCurrency(row.getValue('receivables'))}`
    },
    {
        id: 'actions',
        header: ''
    }
]
</script>

<template>
    <UTable :data="data" :columns="columns" sticky class="overflow-y-auto h-full">
        <template #actions-cell="{ row }">
            <slot name="actions" :item="row.original" :index="row.index" />
        </template>
    </UTable>
</template>