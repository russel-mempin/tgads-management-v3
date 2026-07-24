<script setup lang="ts">
import { onMounted, ref, h, resolveComponent } from 'vue'
import { getAllVoidedJobs } from '@/api/voided_jobs';
import type { VoidedJobs } from '@/types/voided_jobsTypes';
import type { TableColumn } from '@nuxt/ui';
import { formatDate } from '@/utils/formatters';

const data = ref<VoidedJobs[]>([])
const loading = ref(false)
const UTooltip = resolveComponent('UTooltip')

const fetchData = async () => {
    data.value = await getAllVoidedJobs()
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
        accessorKey: 'job_date',
        header: 'Date Received',
        cell: ({ row }) => `${formatDate(row.getValue('job_date'))}`
    },
    {
        accessorKey: 'voided_at',
        header: 'Date Voided',
        cell: ({ row }) => `${formatDate(row.getValue('voided_at'))}`
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
        accessorKey: 'voided_by_name',
        header: 'Voided By',
        cell: ({ row }) => `${row.getValue('voided_by_name')}`
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