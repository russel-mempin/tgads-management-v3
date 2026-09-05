<script setup lang="ts">
import { onMounted, ref, h, resolveComponent, computed, watch } from 'vue'
import { getAllForReview, getForReviewCount } from '@/api/forReviews';
import type { ForReview } from '@/types/forReview';
import type { TableColumn } from '@nuxt/ui';
import { useRouter } from 'vue-router';

const router = useRouter()
const data = ref<ForReview[]>([])
const loading = ref(false)
const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UTooltip = resolveComponent('UTooltip')

// Pagination
const currentPage = ref(1)
const rows = ref(20)
const totalRecords = ref(0)
const currentOffset = computed(() => (currentPage.value - 1) * rows.value)

const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getAllForReview(
            currentOffset.value,
            rows.value
        )
        totalRecords.value = await getForReviewCount()
    }
    finally {
        loading.value = false
    }
}

watch([currentPage, rows], fetchData)

onMounted(fetchData)

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
        <div class="h-full min-h-0 flex flex-col">
            <section v-if="!loading" class="flex-1 min-h-0 m-6 border border-default rounded-md overflow-hidden">
                <UTable sticky class="overflow-y-auto h-full" :data="data" :columns="columns" :ui="{
                    th: 'text-muted font-semibold uppercase',
                    td: 'text-base text-highlighted',
                    tr: 'hover:bg-elevated/100 odd:bg-elevated/50 cursor-pointer'
                }" />
            </section>

            <section class="shrink-0 mb-4 flex items-center justify-between px-6">
                <p class="text-muted text-sm">
                    Showing
                    {{ data.length ? currentOffset + 1 : 0 }}–{{
                        Math.min(currentOffset + data.length, totalRecords)
                    }}
                    of {{ totalRecords }}
                </p>

                <UPagination v-model:page="currentPage" :total="totalRecords" :items-per-page="rows" />
            </section>
        </div>
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