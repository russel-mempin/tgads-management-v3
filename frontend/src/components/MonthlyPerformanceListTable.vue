<script setup lang="ts">
import { h, resolveComponent, ref } from 'vue';
import type { TableColumn } from '@nuxt/ui';
import { formatCurrency } from '@/utils/formatters';
import { getMonthlyPerformance } from '@/api/performances';
import type { MonthlyPerformanceBase, MonthlyPerformance } from '@/types/performance';

const props = defineProps<{
    data: MonthlyPerformanceBase[]
    year: number
}>()

const UButton = resolveComponent('UButton')

const details = ref<Record<string, MonthlyPerformance>>({})
const loadingMonths = ref<string[]>([])
const expanded = ref({})

const getKey = (month: string) => `${props.year}-${Number(month)}`

const toggleRow = async (row: any) => {
    const isExpanded = row.getIsExpanded()

    row.toggleExpanded()

    // Don't fetch when collapsing
    if (isExpanded) return

    const month = row.original.month
    const key = getKey(month)

    // Don't fetch again if already loaded or currently loading
    if (details.value[key] || loadingMonths.value.includes(key)) return

    loadingMonths.value.push(key)

    try {
        const result = await getMonthlyPerformance(props.year, month)

        console.log('API result:', result)

        details.value[key] = result
    } catch (error) {
        console.error('Failed to fetch monthly performance:', error)
    } finally {
        loadingMonths.value = loadingMonths.value.filter(m => m !== key)
    }
}

const columns: TableColumn<MonthlyPerformanceBase>[] = [
    {
        id: 'expand',
        cell: ({ row }) =>
            h(UButton, {
                color: 'neutral',
                variant: 'ghost',
                icon: 'i-lucide-chevron-down',
                square: true,
                'aria-label': 'Expand',
                onClick: () => toggleRow(row),
                ui: {
                    leadingIcon: [
                        'transition-transform',
                        row.getIsExpanded() ? 'duration-200 rotate-180' : ''
                    ]
                },
            })
    },
    {
        accessorKey: 'month',
        header: 'Month',
    },
    {
        accessorKey: 'collected',
        header: 'Collected',
        cell: ({ row }) => formatCurrency(row.getValue('collected'))
    },
    {
        accessorKey: 'expenses',
        header: 'Expenses',
        cell: ({ row }) => formatCurrency(row.getValue('expenses'))
    },
    {
        accessorKey: 'net',
        header: 'Net',
        cell: ({ row }) => formatCurrency(row.getValue('net'))
    },
    {
        accessorKey: 'sales',
        header: 'Sales',
        cell: ({ row }) => formatCurrency(row.getValue('sales'))
    },
    {
        accessorKey: 'receivables',
        header: 'Receivables',
        cell: ({ row }) => formatCurrency(row.getValue('receivables'))
    },
    {
        id: 'actions',
        header: ''
    }
]
</script>

<template>
    <UTable v-model:expanded="expanded" :data="data" :columns="columns" :get-row-can-expand="() => true" sticky
        class="overflow-y-auto h-full">
        <template #expanded="{ row }">
            <div class="p-4">
                <p>Expanded: {{ row.original.month }}</p>

                <div v-if="loadingMonths.includes(getKey(row.original.month.toString()))">
                    Loading details...
                </div>

                <div v-else-if="details[getKey(row.original.month.toString())]">
                    <pre>{{ details[getKey(row.original.month.toString())] }}</pre>
                </div>

                <div v-else>
                    No details loaded.
                </div>
            </div>
        </template>

        <template #actions-cell="{ row }">
            <slot name="actions" :item="row.original" :index="row.index" />
        </template>
    </UTable>
</template>