<script setup lang="ts">
import { computed } from 'vue';
import type { Expense } from '@/types/expense';
import VueApexCharts from 'vue3-apexcharts'

const props = defineProps<{
    data: Expense[]
}>()

const groupedExpenses = computed(() => {
    return props.data.reduce((acc, expense) => {
        const category = expense.category
        const amount = Number(expense.amount)

        acc[category] = (acc[category] || 0) + amount

        return acc
    }, {} as Record<string, number>)
})

const series = computed(() => Object.values(groupedExpenses.value))

const chartOptions = computed(() => ({
    chart: {
        type: 'pie' as const,
    },
    labels: Object.keys(groupedExpenses.value),
    legend: {
        position: 'bottom' as const,
    },
    dataLabels: {
        formatter: (percentage: number) => `${percentage.toFixed(1)}%`,
    },
    tooltip: {
        y: {
            formatter: (value: number) =>
                `₱${value.toLocaleString('en-PH', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                })}`,
        },
    },
}))
</script>

<template>
    <VueApexCharts type="pie" height="350" :options="chartOptions" :series="series" />
</template>