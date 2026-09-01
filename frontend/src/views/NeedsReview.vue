<script setup lang="ts">
import { onMounted, ref, h, resolveComponent } from 'vue'
import { getAllForReview } from '@/api/forReviews';
import type { ForReview } from '@/types/forReview';
import type { TableColumn } from '@nuxt/ui';
import { useRouter } from 'vue-router';

const router = useRouter()
const data = ref<ForReview[]>([])
const loading = ref(false)
const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UTooltip = resolveComponent('UTooltip')

const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getAllForReview()
    }
    finally {
        loading.value = false
    }
}

onMounted(async () => {
    fetchData()
})

const columns: TableColumn<ForReview>[] = [
    {
        accessorKey: 'entity_reference',
        header: 'ID',
        cell: ({ row }) => `${row.getValue('entity_reference')}`
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

            return h(UBadge, { color }, () =>
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
                h('span', { class: 'truncate block max-w-120 cursor-help' }, reason)
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
                        if (row.original.entity_type === "Job Order") {
                            router.push(`/review-data/job-orders/${row.original.entity_id}`)
                        }
                        else if (row.original.entity_type === "Payment") {
                            router.push(`review-data/payments/${row.original.entity_id}`)
                        }
                        else if (row.original.entity_type === "Job Item") {
                            router.push(`/review-data/job-items/${row.original.entity_id}`)
                        }
                    }
                }),
            ])
    }
]
</script>

<template>
    <Transition name="fade" mode="out-in">
        <section v-if="!loading" class="m-6 border border-default rounded-md">
            <UTable :data="data" :columns="columns" :ui="{
                th: 'text-muted font-semibold uppercase',
                td: 'text-base text-highlighted',
                tr: 'hover:bg-elevated/100 odd:bg-elevated/50 cursor-pointer'
            }" />
        </section>
    </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>