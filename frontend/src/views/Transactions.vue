<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import type { TRANSACTION_CATEGORIES, DATE_PERIODS } from '@/utils/constants';
import type { Transaction } from '@/types/transaction';
import { getAllTransactions } from '@/api/transaction';
import TransactionsTable from '@/components/TransactionsTable.vue';

const data = ref<Transaction[]>([])

// Filter Variables
const period = ref<DATE_PERIODS>('this_month')
const category = ref<TRANSACTION_CATEGORIES | 'all'>('all')

// Pagination Variables
const currentPage = ref(1)
const rows = ref(10)
const totalRecords = ref(0)
const currentOffset = computed(() => (currentPage.value - 1) * rows.value)

// UI Variables
const loading = ref(false)
const periods: { label: string; value: DATE_PERIODS }[] = [
    { label: 'Today', value: 'today' },
    { label: 'This Week', value: 'this_week' },
    { label: 'This Month', value: 'this_month' },
    { label: 'Last Month', value: 'last_month' },
    { label: 'This Year', value: 'this_year' },
    { label: 'All Time', value: 'all' },
]

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getAllTransactions(
            period.value,
            category.value === 'all' ? undefined : category.value,
            currentOffset.value,
            rows.value
        )
        console.log(data.value)
    }
    finally {
        loading.value = false
    }
}
onMounted(fetchData)
watch(
    [period, category],
    () => {
        currentPage.value = 1
        fetchData()
    }
)

watch(
    [currentPage, rows],
    fetchData
)
</script>

<template>
    <section class="shrink-0 mx-6 mt-6 flex gap-2">
        <UButton v-for="item in periods" :key="item.value" :label="item.label" class="rounded-full"
            :variant="period === item.value ? 'solid' : 'outline'" @click="period = item.value" />
    </section>
    <section class="mx-6 mt-6 border border-default bg-default rounded-md">
        <div class="flex p-4 border-b border-default">
            <USelect class="flex-1" />
        </div>
        <TransactionsTable :data="data" />
        <div class="border-t border-default flex items-center justify-between p-4">
            <p class="text-muted text-sm">
                Showing
                {{ data.length ? currentOffset + 1 : 0 }}–{{
                    Math.min(currentOffset + data.length, totalRecords)
                }}
                of {{ totalRecords }}
            </p>
            <UPagination v-model:page="currentPage" :total="totalRecords" :items-per-page="rows" />
        </div>
    </section>
</template>