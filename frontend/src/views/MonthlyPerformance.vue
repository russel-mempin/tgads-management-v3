<script setup lang="ts">
// TODO: Monthly sales and expenses
// TODO: Change to perfomance report
// TODO: Yearly performance per month income expense side by side
// TODO: When clicked, show details
// Top customers, top products
import { ref, watch } from 'vue';
import MonthlyPerformanceListTable from '@/components/MonthlyPerformanceListTable.vue';
import { getMonthlyPerformanceList } from '@/api/performances'
import type { MonthlyPerformanceBase } from '@/types/performance';

const loading = ref(false)

const data = ref<MonthlyPerformanceBase[]>([])
const yearToSearch = ref(2026)

// UI Variables
const periods: { label: string; value: number }[] = [
    { label: '2026', value: 2026 },
    { label: '2027', value: 2027 },
]

const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getMonthlyPerformanceList(yearToSearch.value)
    }
    finally {
        loading.value = false
    }
}

watch(yearToSearch, fetchData, { immediate: true })
</script>

<template>
    <div class="h-full min-h-0 flex flex-col">
        <section class="shrink-0 mt-6 px-6 flex gap-4 items-center">
            <UButton v-for="item in periods" :key="item.value" :label="item.label" class="rounded-full"
                :variant="yearToSearch === item.value ? 'solid' : 'outline'"
                @click="() => { yearToSearch = item.value }" />
        </section>
        <section class="bg-default flex-1 min-h-0 m-6 border border-default rounded-md overflow-hidden">
            <MonthlyPerformanceListTable :data="data" :year="yearToSearch" />
        </section>
    </div>
</template>