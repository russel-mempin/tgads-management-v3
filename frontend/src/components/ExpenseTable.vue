<script setup lang="ts">
import { resolveComponent, h } from 'vue';
import type { Expense } from '@/types/expense';
import type { TableColumn } from '@nuxt/ui';
import type { TableMeta, Row } from '@tanstack/vue-table'
import { formatDate, formatCurrency, mapExpenseCategory } from '@/utils/formatters';

const UBadge = resolveComponent('UBadge')

const props = defineProps<{
    expense: Expense[]
}>()

const columns: TableColumn<Expense>[] = [
    {
        accessorKey: 'date',
        header: 'Date',
        cell: ({ row }) => `${formatDate(row.getValue('date'))}`
    },
    {
        accessorKey: 'category',
        header: 'Category',
        cell: ({ row }) => {
            const category = row.getValue('category') as string
            return h(UBadge, { class: mapExpenseCategory(category) },
                () => category
            )
        }
    },
    {
        accessorKey: 'description',
        header: 'Description',
    },
    {
        accessorKey: 'amount',
        header: 'Amount',
        cell: ({ row }) => h(
            'span',
            { class: 'font-semibold text-red-600' },
            formatCurrency(row.getValue('amount'))
        )
    },
    {
        accessorKey: 'account_name',
        header: 'Method',
    },
    {
        accessorKey: 'created_by_name',
        header: 'Created By',
    },
    {
        id: 'actions',
        header: ''
    }
]

const meta: TableMeta<Expense> = {
    class: {
        tr: () => 'bg-error/10!'
    }
}
</script>

<template>
    <UTable :data="expense" :columns="columns" :meta="meta">
        <template #actions-cell="{ row }">
            <slot name="actions" :item="row.original" :index="row.index" />
        </template>
    </UTable>
</template>