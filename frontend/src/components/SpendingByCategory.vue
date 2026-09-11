<script setup lang="ts">
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts';
import type { ApexOptions } from 'apexcharts'
import type { ExpenseByCategory } from '@/types/expense';
import { mapExpenseCategoryColor } from '@/utils/formatters';

const props = defineProps<{
    data: ExpenseByCategory[]
}>()

const sortedData = computed(() =>
    [...props.data].sort((a, b) => Number(b.amount) - Number(a.amount))
)

const series = computed(() => [
    {
        name: 'Spending',
        data: sortedData.value.map(item => item.amount)
    }
])

const chartOptions = computed<ApexOptions>(() => ({
    chart: {
        type: 'bar',
        toolbar: {
            show: false,
        },
    },

    plotOptions: {
        bar: {
            horizontal: true,
            distributed: true,
            borderRadius: 4,
            barHeight: '60%',
        },
    },

    colors: sortedData.value.map(item =>
        mapExpenseCategoryColor(item.category)
    ),

    xaxis: {
        categories: sortedData.value.map(item => item.category),

        labels: {
            formatter: (value: string) =>
                `₱${Number(value).toLocaleString()}`,
        },
    },

    yaxis: {
        labels: {
            style: {
                fontSize: '13px',
            },
        },
    },

    dataLabels: {
        enabled: true,
        formatter: (value: number) =>
            `₱${value.toLocaleString()}`,
    },

    tooltip: {
        y: {
            formatter: (value: number) =>
                `₱${value.toLocaleString()}`,
        },
    },

    legend: {
        show: false,
    },
}))
</script>

<template>
    <p class="text-lg">Expense By Category</p>
    <div>
        <VueApexCharts type="bar" height="350" :options="chartOptions" :series="series" />
    </div>
</template>