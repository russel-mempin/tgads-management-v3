<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import type { TRANSACTION_CATEGORIES, DATE_PERIODS } from '@/utils/constants';
import type { Transaction } from '@/types/transaction';
import { getAllTransactions } from '@/api/transaction';
import TransactionsTable from '@/components/TransactionsTable.vue';
import { useReferenceStore } from '@/stores/reference';

const referenceStore = useReferenceStore()

const data = ref<Transaction[]>([])

// Filter Variables
const period = ref<DATE_PERIODS>('this_month')
const category = ref<TRANSACTION_CATEGORIES | 'all'>('all')

// Pagination Variables
const currentPage = ref(1)
const rows = ref(20)
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

// Filtering
const categories: { label: string; value: TRANSACTION_CATEGORIES | 'all' }[] = [
    { label: 'All Categories', value: 'all' },
    { label: 'Payment', value: 'payment' },
    { label: 'Expense', value: 'expense' },
    { label: 'Miscellaneous Sale', value: 'misc_sale' },
    { label: 'Transfer', value: 'transfer' },
    { label: 'Adjustment', value: 'adjustment' },
    { label: 'Reversal', value: 'reversal' },
    { label: 'Refund', value: 'refund' },
]
const account = ref<string>('all')

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        const result = await getAllTransactions(
            period.value,
            category.value === 'all' ? undefined : category.value,
            account.value === 'all' ? undefined : account.value,
            currentOffset.value,
            rows.value
        )
        data.value = result.items
        totalRecords.value = result.total
    }
    finally {
        loading.value = false
    }
}
onMounted(fetchData)
watch(
    [period, category, account],
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
    <div class="h-full min-h-0 flex flex-col">
        <section class="shrink-0 mx-6 mt-6 flex gap-2">
            <UButton v-for="item in periods" :key="item.value" :label="item.label" class="rounded-full"
                :variant="period === item.value ? 'solid' : 'outline'" @click="() => { period = item.value }" />
        </section>
        <section class="mx-6 mt-6 mb-6 border border-default bg-default rounded-md flex-1 min-h-0 flex flex-col">
            <div class="shrink-0 grid grid-cols-2 gap-4 p-4 border-b border-default">
                <div class="flex items-center gap-2">
                    <p class="text-muted">Show Only: </p>
                    <USelect class="flex-1" v-model="category" :items="categories" size="lg" />
                </div>
                <div class="flex items-center gap-2">
                    <p class="text-muted">Method: </p>
                    <USelect class="flex-1" v-model="account" value-key="id" label-key="name" :items="[
                        { id: 'all', name: 'All Methods' },
                        ...referenceStore.accountOptions
                    ]" size="lg" />
                </div>
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
    </div>
</template>