<script setup lang="ts">
import { resolveComponent, h } from 'vue'
import { formatCurrency, formatDate, getJobStatusColor } from '@/utils/formatters';
import type { JobItemTableRow } from '@/types/jobOrder';
import type { TableColumn } from '@nuxt/ui';

const UBadge = resolveComponent('UBadge')

const props = defineProps<{
    jobItems?: JobItemTableRow[]
    totalClaimedByItem?: Map<string, number>
    getTotalClaimed?: (itemId: string) => number
}>()
// Table data
const columns: TableColumn<JobItemTableRow>[] = [
    { accessorKey: 'item_id', header: 'ID' },
    {
        accessorKey: 'service_name',
        header: 'Service',
        cell: ({ row }) => {
            const item = row.original
            if (!item.service_name_snapshot) {
                return '—'
            }

            const tooltipParts = [
                item.description ? `Description: ${item.description}` : '',
                item.notes ? `Notes: ${item.notes}` : '',
                ...(item.extras ?? []).map(
                    extra => `${extra.name_snapshot} (${extra.quantity}×)`
                )
            ].filter(Boolean)

            const serviceContent = h('div', {
                class: 'flex items-center gap-1 whitespace-nowrap'
            }, [
                h('span', {}, item.service_name_snapshot),

                item.service_option_name_snapshot
                    ? h(
                        'span',
                        { class: 'text-muted' },
                        `— ${item.service_option_name_snapshot}`
                    )
                    : null
            ])

            if (!tooltipParts.length) {
                return serviceContent
            }

            return h(
                resolveComponent('UTooltip'),
                {
                    text: tooltipParts.join('\n'),
                },
                {
                    default: () => serviceContent
                }
            )
        }
    },
    {
        id: 'size',
        header: 'Size',
        cell: ({ row }) => {
            const item = row.original
            return item.width && item.height
                ? `${item.width} x ${item.height} ${item.size_unit ?? ''}`
                : '—'
        },
    },
    {
        accessorKey: 'quantity',
        header: 'Qty',
        cell: ({ row }) => `${row.original.quantity} pc(s)`
    },
    {
        accessorKey: 'unit_price',
        header: 'Unit Price',
        cell: ({ row }) => `${formatCurrency(row.original.unit_price)}`,
    },
    {
        accessorKey: 'subtotal',
        header: 'Subtotal',
        cell: ({ row }) => h('span', { class: 'font-semibold' }, formatCurrency(row.original.subtotal)),
    },
    { accessorKey: 'due_date', header: 'Due Date', cell: ({ row }) => `${formatDate(row.original.due_date)}`, },
    {
        accessorKey: 'total_claimed',
        header: 'Claimed',
        cell: ({ row }) =>
            `${props.getTotalClaimed?.(row.original.item_id) ?? row.original.total_claimed} / ${row.original.quantity}`
    },
    {
        accessorKey: 'job_status',
        header: 'Status',
        cell: ({ row }) => {
            return h(UBadge, { color: getJobStatusColor(row.original.job_status) }, () =>
                row.getValue('job_status')
            )
        }
    },
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
                <UIcon name="i-lucide-briefcase" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                <h2 class="text-highlighted font-semibold">Job Items</h2>
            </div>
            <slot name="header-actions" />
        </div>
        <UTable :data="props.jobItems" :columns="columns">
            <template #actions-cell="{ row }">
                <slot name="actions" :item="row.original" :index="row.index" />
            </template>
            <template #empty>
                <div class="flex flex-col items-center justify-center py-12 text-center px-6">
                    <div class="w-12 h-12 rounded-full bg-elevated flex items-center justify-center mb-3">
                        <UIcon name="i-lucide-package-open" class="size-6 text-muted" />
                    </div>
                    <p class="font-medium text-highlighted mb-1">No items yet</p>
                    <p class="text-sm text-muted">Click "Add Item" to start building this job order.</p>
                </div>
            </template>
        </UTable>
    </section>
</template>