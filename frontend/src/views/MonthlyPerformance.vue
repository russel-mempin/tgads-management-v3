<script setup lang="ts">
// TODO: Monthly sales and expenses
// TODO: Change to perfomance report
// TODO: Yearly performance per month income expense side by side
// TODO: When clicked, show details
// Top customers, top products
import { ref, onMounted } from 'vue';
import MonthlyPerformanceListTable from '@/components/MonthlyPerformanceListTable.vue';
import { getMonthlyPerformanceList } from '@/api/performances'
import type { MonthlyPerformanceBase } from '@/types/performance';

const loading = ref(false)

const data = ref<MonthlyPerformanceBase[]>([])
const yearToSearch = ref(2026)

const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getMonthlyPerformanceList("2026")
        console.log(data.value)
    }
    finally {
        loading.value = false
    }
}

onMounted(async () => {
    await fetchData()
})
</script>

<template>
    <div>
        <UInput size="lg" class="flex-1" v-model="yearToSearch" placeholder="Search by description" />
    </div>
    <MonthlyPerformanceListTable :data="data" />
</template>