<script setup lang="ts">
import { h } from 'vue';
import type { Transaction } from '@/types/transaction';
import type { TableColumn } from '@nuxt/ui';
import type { TableMeta, Row } from '@tanstack/vue-table'
import { formatDate, formatCurrency } from '@/utils/formatters';

const props = defineProps<{
    data: Transaction[]
}>()

const columns: TableColumn<Transaction>[] = [
    {
        accessorKey: 'date',
        header: 'Date',
        cell: ({ row }) => `${formatDate(row.getValue('date'))}`
    },
    {
        accessorKey: 'source_type',
        header: 'Category',
    },
    {
        accessorKey: 'amount',
        header: 'Amount',
        meta: {
            class: { td: 'font-semibold' }
        },
        cell: ({ row }) => {
            const amount = Number.parseFloat(row.getValue('amount'))
            return h('span', {
                class: amount < 0 ? 'text-red-600' : 'text-green-600'
            }, formatCurrency(amount))
        }
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

const meta: TableMeta<Transaction> = {
    class: {
        tr: (row: Row<Transaction>) => {
            const amount = Number.parseFloat(row.original.amount)
            return amount < 0 ? 'bg-error/10!' : 'bg-success/10!'
        }
    }
}
</script>

<template>
    <UTable :data="data" :columns="columns" :meta="meta">
        <template #actions-cell="{ row }">
            <slot name="actions" :item="row.original" :index="row.index" />
        </template>
    </UTable>
</template>