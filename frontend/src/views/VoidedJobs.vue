<script setup lang="ts">
import { onMounted, ref, h, resolveComponent } from 'vue'
import { getAllVoidedJobs } from '@/api/jobOrders';
import type { VoidedJobs } from '@/types/voidedJob';
import type { TableColumn } from '@nuxt/ui';
import { formatDate } from '@/utils/formatters';

const data = ref<VoidedJobs[]>([])
const loading = ref(false)
const UTooltip = resolveComponent('UTooltip')

const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getAllVoidedJobs()
    }
    finally {
        loading.value = false
    }
}

onMounted(async () => {
    fetchData()
})

const columns: TableColumn<VoidedJobs>[] = [
    {
        accessorKey: 'jo_number',
        header: '#',
        cell: ({ row }) => `#${row.getValue('jo_number')}`
    },
    {
        accessorKey: 'date_received',
        header: 'Date Received',
        cell: ({ row }) => `${formatDate(row.getValue('date_received'))}`
    },
    {
        accessorKey: 'voided_at',
        header: 'Date Voided',
        cell: ({ row }) => `${formatDate(row.getValue('voided_at'))}`
    },
    {
        accessorKey: 'void_reason',
        header: 'Reason',
        cell: ({ row }) => {
            const reason = row.getValue('void_reason') as string

            return h(UTooltip, { text: reason, delayDuration: 300 }, () =>
                h(
                    'span',
                    { class: 'truncate block max-w-72 cursor-help' },
                    reason
                )
            )
        }
    },
    {
        accessorKey: 'voided_by_name',
        header: 'Voided By',
        cell: ({ row }) => `${row.getValue('voided_by_name')}`
    }
]
</script>

<template>
    <Transition name="fade" mode="out-in">
        <section class="m-6 border border-default rounded-md">
            <UTable :data="data" :columns="columns" :loading="loading" :ui="{
                th: 'text-muted font-semibold uppercase',
                td: 'text-base text-highlighted',
                tr: 'hover:bg-elevated/100 odd:bg-elevated/50 cursor-pointer'
            }" />
        </section>
    </Transition>
    <!-- <section class="mt-4 flex items-center justify-between">
        <p class="text-muted text-sm">
            Showing {{ job_orders.length ? currentOffset + 1 : 0 }}–{{ Math.min(currentOffset + rows, totalRecords) }}
            of {{ totalRecords }}
        </p>
        <UPagination v-model:page="currentPage" :total="totalRecords" :items-per-page="rows" />
    </section> -->
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