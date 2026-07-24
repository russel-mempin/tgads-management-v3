<script setup lang="ts">
import { onMounted, ref, h, resolveComponent } from 'vue'
import { getAllForReview } from '@/api/for_reviews';
import type { ForReview } from '@/types/for_reviewTypes';
import type { TableColumn } from '@nuxt/ui';
import { useRouter } from 'vue-router';

const router = useRouter()
const data = ref<ForReview[]>([])
const loading = ref(false)
const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UTooltip = resolveComponent('UTooltip')

const fetchData = async () => {
    data.value = await getAllForReview()
    console.log(data.value)
}

onMounted(async () => {
    fetchData()
})

const columns: TableColumn<ForReview>[] = [
    {
        accessorKey: 'entity_reference',
        header: '#',
        cell: ({ row }) => `#${row.getValue('entity_reference')}`
    },
    {
        accessorKey: 'entity_type',
        header: 'Type',
        cell: ({ row }) => `${row.getValue('entity_type')}`
    },
    {
        accessorKey: 'reason_category',
        header: 'Category',
        cell: ({ row }) => {
            const color = {
                'Missing Data': 'warning' as const,
                'Pricing Discrepancy': 'error' as const,
                'Status Issue': 'info' as const,
                'Needs Verification': 'neutral' as const,
            }[row.getValue('reason_category') as string]

            return h(UBadge, { class: 'capitalize font-semibold', variant: 'soft', color }, () =>
                row.getValue('reason_category')
            )
        }
    },
    {
        accessorKey: 'reason',
        header: 'Reason',
        cell: ({ row }) => {
            const reason = row.getValue('reason') as string
            return h(UTooltip, { text: reason, delayDuration: 300 }, () =>
                h('span', { class: 'truncate block max-w-72 cursor-help' }, reason)
            )
        }
    },
    {
        accessorKey: 'created_by_name',
        header: 'Flagged by',
        cell: ({ row }) => `${row.getValue('created_by_name')}`
    },
    {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) =>
            h('div', { class: 'flex items-center gap-2' }, [
                h(UButton, {
                    color: 'neutral',
                    variant: 'outline',
                    icon: 'i-lucide-eye',
                    label: 'View',
                    size: 'md',
                    onClick: (event: Event) => {
                        event.stopPropagation()
                        router.push(`/job-orders/view/${row.original.entity_reference}`)
                    }
                }),
            ])
    }
]
</script>

<template>
    <section class="border border-default rounded-md">
        <UTable :data="data" :columns="columns" :loading="loading" :ui="{
            th: 'text-muted font-semibold uppercase',
            td: 'text-base text-highlighted',
            tr: 'hover:bg-elevated/100 odd:bg-elevated/50 cursor-pointer'
        }" />
    </section>
    <!-- <section class="mt-4 flex items-center justify-between">
        <p class="text-muted text-sm">
            Showing {{ job_orders.length ? currentOffset + 1 : 0 }}–{{ Math.min(currentOffset + rows, totalRecords) }}
            of {{ totalRecords }}
        </p>
        <UPagination v-model:page="currentPage" :total="totalRecords" :items-per-page="rows" />
    </section> -->
</template>